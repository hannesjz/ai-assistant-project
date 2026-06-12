import SwiftUI

/// Floating bubble that shows the answer index when the app is used in Split View or Slide Over.
/// This view is for in-app display only — the notification banner covers the cross-app case.
struct AnswerOverlayView: View {

    let answerIndex: Int
    @Binding var isVisible: Bool

    private let colors: [Color] = [.blue, .green, .orange, .purple]

    var body: some View {
        ZStack {
            Circle()
                .fill(colors[safe: answerIndex - 1] ?? .blue)
                .frame(width: 56, height: 56)
                .shadow(radius: 6)

            Text("\(answerIndex)")
                .font(.system(size: 26, weight: .bold, design: .rounded))
                .foregroundColor(.white)
        }
        .onTapGesture { isVisible = false }
        .transition(.scale.combined(with: .opacity))
        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isVisible)
    }
}

// MARK: - Safe subscript (local copy for this file's scope)

private extension Array {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
