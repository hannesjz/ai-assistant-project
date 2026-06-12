import Foundation

struct QuizQuestion {
    let question: String
    let options: [String]
    let rawOCRText: String
}

struct QuizResult {
    let question: QuizQuestion
    let answerIndex: Int      // 1-4
    let answerText: String
    let processingTime: TimeInterval
    let timestamp: Date
}

enum QuizError: LocalizedError {
    case noAPIKey
    case apiError(statusCode: Int)
    case invalidResponse(text: String)
    case ocrFailed
    case noQuizDetected
    case networkError(Error)

    var errorDescription: String? {
        switch self {
        case .noAPIKey:          return "Ange din Anthropic API-nyckel i inställningarna"
        case .apiError(let c):   return "API-fel (kod \(c)) – kolla nyckeln"
        case .invalidResponse:   return "Oväntat svar från AI"
        case .ocrFailed:         return "Kunde inte läsa texten i skärmbilden"
        case .noQuizDetected:    return "Hittade ingen quiz i skärmbilden"
        case .networkError(let e): return "Nätverksfel: \(e.localizedDescription)"
        }
    }
}
