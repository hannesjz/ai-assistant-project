import Foundation

// MARK: - Response models

private struct AnthropicResponse: Decodable {
    let content: [ContentBlock]
    let stopReason: String?

    struct ContentBlock: Decodable {
        let type: String
        let text: String?
    }

    enum CodingKeys: String, CodingKey {
        case content
        case stopReason = "stop_reason"
    }
}

private struct AnthropicError: Decodable {
    let error: APIError
    struct APIError: Decodable { let message: String }
}

// MARK: - Client

/// Calls Claude Haiku 4.5 – the fastest and cheapest Claude model (ideal for real-time quiz solving).
/// Average response time: ~300–700ms on a good connection.
class ClaudeAPIClient {

    static let shared = ClaudeAPIClient()

    private let endpoint = URL(string: "https://api.anthropic.com/v1/messages")!
    private var apiKey: String = UserDefaults.standard.string(forKey: "anthropic_api_key") ?? ""

    func configure(apiKey: String) {
        self.apiKey = apiKey
        UserDefaults.standard.set(apiKey, forKey: "anthropic_api_key")
    }

    /// Sends the raw OCR text to Claude and returns the answer index (1-4).
    func solveQuiz(ocrText: String) async throws -> (answerIndex: Int, answerLabel: String) {
        guard !apiKey.isEmpty else { throw QuizError.noAPIKey }

        let prompt = """
        Below is OCR text extracted from a quiz app screenshot on an iPhone.
        The screen shows a multiple choice question with exactly 4 answer alternatives.

        OCR TEXT:
        \(ocrText)

        Instructions:
        1. Identify the quiz question.
        2. Identify the 4 answer alternatives (they may be labeled A/B/C/D, 1/2/3/4, or unlabeled).
        3. Determine the correct answer.
        4. Reply with ONLY a single digit: 1, 2, 3 or 4 (where 1=first option, 2=second, 3=third, 4=fourth).

        Single digit only. Nothing else.
        """

        let body: [String: Any] = [
            "model": "claude-haiku-4-5",
            "max_tokens": 5,
            "messages": [["role": "user", "content": prompt]]
        ]

        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        request.timeoutInterval = 12
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, urlResponse) = try await URLSession.shared.data(for: request)

        guard let http = urlResponse as? HTTPURLResponse else {
            throw QuizError.networkError(URLError(.badServerResponse))
        }
        guard http.statusCode == 200 else {
            throw QuizError.apiError(statusCode: http.statusCode)
        }

        let decoded = try JSONDecoder().decode(AnthropicResponse.self, from: data)
        guard let rawText = decoded.content.first?.text else {
            throw QuizError.invalidResponse(text: "empty content")
        }

        let trimmed = rawText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let index = Int(trimmed), (1...4).contains(index) else {
            throw QuizError.invalidResponse(text: trimmed)
        }

        let labels = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        return (index, labels[index - 1])
    }
}
