import Vision
import UIKit

/// Extracts all text from a UIImage using Apple's on-device Vision framework.
/// Typical processing time: 100-300ms on modern iPhones.
class OCRService {

    static let shared = OCRService()

    func extractText(from image: UIImage) async throws -> String {
        guard let cgImage = image.cgImage else { throw QuizError.ocrFailed }

        return try await withCheckedThrowingContinuation { continuation in
            let request = VNRecognizeTextRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                let text = (request.results as? [VNRecognizedTextObservation] ?? [])
                    .compactMap { $0.topCandidates(1).first?.string }
                    .joined(separator: "\n")
                continuation.resume(returning: text)
            }
            request.recognitionLevel = .accurate
            request.usesLanguageCorrection = true

            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            do {
                try handler.perform([request])
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }
}
