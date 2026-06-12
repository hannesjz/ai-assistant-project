import UserNotifications
import UIKit

/// Delivers the quiz answer as a local notification banner visible on top of any app.
class NotificationService {

    static let shared = NotificationService()

    private let answerCategory = "QUIZ_ANSWER"

    func requestPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }

    /// Shows "Answer: 2️⃣" as an immediate notification banner (~0 delay).
    func showAnswer(answerIndex: Int, time: TimeInterval) {
        let labels = ["1️⃣ Svar 1", "2️⃣ Svar 2", "3️⃣ Svar 3", "4️⃣ Svar 4"]
        let label = labels[safe: answerIndex - 1] ?? "\(answerIndex)"
        let ms = Int(time * 1000)

        let content = UNMutableNotificationContent()
        content.title = "Quiz Solver ✅"
        content.body = "\(label)  •  \(ms) ms"
        content.sound = .default
        content.interruptionLevel = .timeSensitive   // pops above all apps on iOS 15+

        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: nil   // nil = immediate
        )

        UNUserNotificationCenter.current().add(request) { _ in }

        // Also remove old answer notifications to keep it clean
        UNUserNotificationCenter.current().removeDeliveredNotifications(
            withIdentifiers: ["quiz_last"]
        )
    }
}

private extension Array {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
