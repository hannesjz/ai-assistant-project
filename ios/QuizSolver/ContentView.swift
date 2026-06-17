import SwiftUI

struct ContentView: View {

    @StateObject private var monitor = LiveScreenMonitor()
    @State private var apiKey = UserDefaults.standard.string(forKey: "anthropic_api_key") ?? ""
    @State private var showAPIKeyField = false

    var body: some View {
        NavigationView {
            VStack(spacing: 24) {

                statusCard

                if showAPIKeyField {
                    apiKeySection
                }

                monitorButton

                if let result = monitor.lastResult {
                    ResultCard(result: result)
                }

                if let error = monitor.errorMessage {
                    ErrorBanner(message: error)
                }

                Spacer()

                instructions

            }
            .padding()
            .navigationTitle("Quiz Solver")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showAPIKeyField.toggle()
                    } label: {
                        Image(systemName: "key.fill")
                            .foregroundColor(apiKey.isEmpty ? .red : .secondary)
                    }
                }
            }
        }
    }

    // MARK: - Sub-views

    private var statusCard: some View {
        HStack {
            Circle()
                .fill(monitor.isMonitoring ? Color.green : Color.gray)
                .frame(width: 12, height: 12)
                .scaleEffect(monitor.isProcessing ? 1.4 : 1.0)
                .animation(.easeInOut(duration: 0.5).repeatWhileTrue(autoreverses: true, condition: monitor.isProcessing), value: monitor.isProcessing)

            Text(statusText)
                .font(.subheadline)
                .foregroundColor(.secondary)

            Spacer()
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }

    private var statusText: String {
        if monitor.isProcessing { return "Analyserar skärmbild..." }
        if monitor.isMonitoring  { return "Lyssnar efter skärmbilder..." }
        return "Ej aktivt"
    }

    private var apiKeySection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Anthropic API-nyckel")
                .font(.caption)
                .foregroundColor(.secondary)

            SecureField("sk-ant-...", text: $apiKey)
                .textFieldStyle(.roundedBorder)
                .autocorrectionDisabled()
                .textInputAutocapitalization(.never)
                .onChange(of: apiKey) { newValue in
                    ClaudeAPIClient.shared.configure(apiKey: newValue)
                }
        }
    }

    private var monitorButton: some View {
        Button {
            if monitor.isMonitoring {
                monitor.stop()
            } else {
                monitor.start()
            }
        } label: {
            Label(
                monitor.isMonitoring ? "Stoppa" : "Starta Quiz Solver",
                systemImage: monitor.isMonitoring ? "stop.circle.fill" : "play.circle.fill"
            )
            .frame(maxWidth: .infinity)
            .padding()
            .background(monitor.isMonitoring ? Color.red : Color.blue)
            .foregroundColor(.white)
            .cornerRadius(14)
            .font(.headline)
        }
    }

    private var instructions: some View {
        VStack(alignment: .leading, spacing: 6) {
            Label("Hur det fungerar", systemImage: "info.circle")
                .font(.caption.bold())
                .foregroundColor(.secondary)

            Text("1. Starta Quiz Solver och godkänn skärminspelning\n2. Öppna quiz-appen – Quiz Solver läser skärmen live\n3. Svaret visas automatiskt som en notis inom ~1 sekund")
                .font(.caption)
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding()
        .background(Color(.tertiarySystemBackground))
        .cornerRadius(10)
    }
}

// MARK: - Result Card

struct ResultCard: View {
    let result: QuizResult

    var body: some View {
        HStack {
            Text(result.answerText)
                .font(.system(size: 44))

            VStack(alignment: .leading) {
                Text("Alternativ \(result.answerIndex)")
                    .font(.title3.bold())
                Text(String(format: "%.0f ms", result.processingTime * 1000))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
        .padding()
        .background(Color.green.opacity(0.15))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.green.opacity(0.4), lineWidth: 1)
        )
    }
}

// MARK: - Error Banner

struct ErrorBanner: View {
    let message: String

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.orange)
            Text(message)
                .font(.caption)
                .foregroundColor(.primary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.orange.opacity(0.1))
        .cornerRadius(10)
    }
}

// MARK: - Animation helper

private extension Animation {
    func repeatWhileTrue(autoreverses: Bool, condition: Bool) -> Animation {
        condition ? self.repeatForever(autoreverses: autoreverses) : self
    }
}
