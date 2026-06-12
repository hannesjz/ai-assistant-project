import ReplayKit
import UIKit

/// Captures the live screen via ReplayKit and automatically detects quiz questions.
/// The user grants permission once; no manual screenshots needed.
@MainActor
class LiveScreenMonitor: NSObject, ObservableObject {

    @Published var isMonitoring = false
    @Published var lastResult: QuizResult?
    @Published var isProcessing = false
    @Published var errorMessage: String?

    private var lastOCRText = ""
    private var lastAPICallTime: Date = .distantPast
    private let minAPIInterval: TimeInterval = 3.0

    // Coarse frame throttle — read/written on ReplayKit's background thread only.
    // The racy write is intentional: the worst case is two frames slip through at once.
    nonisolated(unsafe) private var lastFrameTime: TimeInterval = 0
    private static let frameInterval: TimeInterval = 1.0   // at most 1 OCR run per second

    // MARK: - Public

    func start() {
        guard RPScreenRecorder.isAvailable else {
            errorMessage = "Skärminspelning stöds ej på denna enhet"
            return
        }

        RPScreenRecorder.shared().startCapture(
            handler: { [weak self] buffer, type, _ in
                self?.didReceiveFrame(buffer, type: type)
            },
            completionHandler: { [weak self] error in
                Task { @MainActor [weak self] in
                    if let error {
                        self?.errorMessage = "Skärminspelning misslyckades: \(error.localizedDescription)"
                    } else {
                        self?.isMonitoring = true
                    }
                }
            }
        )
    }

    func stop() {
        RPScreenRecorder.shared().stopCapture { _ in }
        isMonitoring = false
    }

    // MARK: - Frame handling (called on ReplayKit background thread)

    private nonisolated func didReceiveFrame(_ buffer: CMSampleBuffer, type: RPSampleBufferType) {
        guard type == .video else { return }

        let now = CACurrentMediaTime()
        guard now - lastFrameTime >= Self.frameInterval else { return }
        lastFrameTime = now

        guard let pixelBuffer = CMSampleBufferGetImageBuffer(buffer) else { return }
        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
        guard let cgImage = CIContext().createCGImage(ciImage, from: ciImage.extent) else { return }
        let image = UIImage(cgImage: cgImage)

        Task { @MainActor [weak self] in
            await self?.processFrame(image: image)
        }
    }

    // MARK: - Pipeline (MainActor)

    private func processFrame(image: UIImage) async {
        guard !isProcessing,
              Date().timeIntervalSince(lastAPICallTime) >= minAPIInterval else { return }

        do {
            let ocrText = try await OCRService.shared.extractText(from: image)
            guard !ocrText.isEmpty else { return }
            guard isNewQuestion(ocrText) else { return }

            isProcessing = true
            lastAPICallTime = Date()
            lastOCRText = ocrText
            errorMessage = nil
            defer { isProcessing = false }

            let start = Date()
            let (answerIndex, answerLabel) = try await ClaudeAPIClient.shared.solveQuiz(ocrText: ocrText)
            let elapsed = Date().timeIntervalSince(start)

            lastResult = QuizResult(
                question: QuizQuestion(question: "", options: [], rawOCRText: ocrText),
                answerIndex: answerIndex,
                answerText: answerLabel,
                processingTime: elapsed,
                timestamp: Date()
            )
            NotificationService.shared.showAnswer(answerIndex: answerIndex, time: elapsed)

        } catch {
            if case QuizError.noQuizDetected = error { return }
            errorMessage = (error as? QuizError)?.errorDescription ?? error.localizedDescription
        }
    }

    /// Returns true when the new OCR text differs enough to represent a new question.
    private func isNewQuestion(_ text: String) -> Bool {
        guard !lastOCRText.isEmpty else { return true }
        let old = Set(lastOCRText.lowercased()
            .components(separatedBy: .whitespacesAndNewlines).filter { !$0.isEmpty })
        let new = Set(text.lowercased()
            .components(separatedBy: .whitespacesAndNewlines).filter { !$0.isEmpty })
        let union = old.union(new)
        guard !union.isEmpty else { return false }
        return Double(old.intersection(new).count) / Double(union.count) < 0.75
    }
}
