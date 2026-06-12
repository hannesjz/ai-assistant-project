import Photos
import UIKit

/// Watches the Photo Library for new screenshots and triggers quiz solving.
/// Requires PHAuthorizationStatus.authorized (full access) or .limited.
@MainActor
class ScreenshotMonitor: NSObject, ObservableObject, PHPhotoLibraryChangeObserver {

    @Published var isMonitoring = false
    @Published var lastResult: QuizResult?
    @Published var isProcessing = false
    @Published var errorMessage: String?

    private var lastKnownAssetID: String?

    override init() {
        super.init()
    }

    // MARK: - Public

    func startMonitoring() {
        PHPhotoLibrary.shared().register(self)
        isMonitoring = true
        // Remember the latest asset so we only react to NEW screenshots
        lastKnownAssetID = latestScreenshot()?.localIdentifier
    }

    func stopMonitoring() {
        PHPhotoLibrary.shared().unregisterChangeObserver(self)
        isMonitoring = false
    }

    func requestPermissionAndStart() async {
        let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
        if status == .authorized || status == .limited {
            startMonitoring()
        } else {
            errorMessage = "Fototillgång krävs – aktivera i Inställningar"
        }
    }

    // MARK: - PHPhotoLibraryChangeObserver

    nonisolated func photoLibraryDidChange(_ changeInstance: PHChange) {
        Task { @MainActor in
            guard let asset = latestScreenshot(),
                  asset.localIdentifier != lastKnownAssetID else { return }
            lastKnownAssetID = asset.localIdentifier
            await processScreenshot(asset: asset)
        }
    }

    // MARK: - Private

    private func latestScreenshot() -> PHAsset? {
        let fetchOptions = PHFetchOptions()
        fetchOptions.predicate = NSPredicate(format: "mediaSubtype == %d",
                                             PHAssetMediaSubtype.photoScreenshot.rawValue)
        fetchOptions.sortDescriptors = [NSSortDescriptor(key: "creationDate", ascending: false)]
        fetchOptions.fetchLimit = 1
        return PHAsset.fetchAssets(with: .image, options: fetchOptions).firstObject
    }

    private func processScreenshot(asset: PHAsset) async {
        guard !isProcessing else { return }
        isProcessing = true
        errorMessage = nil

        let start = Date()

        do {
            let image = try await loadImage(from: asset)
            let ocrText = try await OCRService.shared.extractText(from: image)
            guard !ocrText.isEmpty else { throw QuizError.noQuizDetected }

            let (answerIndex, answerLabel) = try await ClaudeAPIClient.shared.solveQuiz(ocrText: ocrText)
            let elapsed = Date().timeIntervalSince(start)

            let question = QuizQuestion(question: "", options: [], rawOCRText: ocrText)
            let result = QuizResult(
                question: question,
                answerIndex: answerIndex,
                answerText: answerLabel,
                processingTime: elapsed,
                timestamp: Date()
            )

            lastResult = result
            NotificationService.shared.showAnswer(answerIndex: answerIndex, time: elapsed)

        } catch {
            errorMessage = (error as? QuizError)?.errorDescription ?? error.localizedDescription
        }

        isProcessing = false
    }

    private func loadImage(from asset: PHAsset) async throws -> UIImage {
        try await withCheckedThrowingContinuation { continuation in
            let options = PHImageRequestOptions()
            options.deliveryMode = .highQualityFormat
            options.isSynchronous = false
            options.resizeMode = .none

            PHImageManager.default().requestImage(
                for: asset,
                targetSize: PHImageManagerMaximumSize,
                contentMode: .aspectFit,
                options: options
            ) { image, _ in
                if let image {
                    continuation.resume(returning: image)
                } else {
                    continuation.resume(throwing: QuizError.ocrFailed)
                }
            }
        }
    }
}
