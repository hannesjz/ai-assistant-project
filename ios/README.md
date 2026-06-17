# QuizSolver – iPhone Quiz Assistant

Solves multiple-choice quiz questions in ~1 second using on-device OCR + Claude Haiku 4.5.

## How it works

1. Tap **Starta Quiz Solver** — iOS asks to allow screen recording (once)
2. Open the quiz app; `RPScreenRecorder` streams live frames to QuizSolver
3. Apple Vision runs OCR on each frame on-device (~100–300 ms)
4. When a new question is detected, Claude Haiku 4.5 picks the answer (~300–700 ms)
5. The answer appears as a notification banner on top of the quiz app

**No manual screenshots needed. Total latency: ~1–1.5 s from question appearing.**

## Setup in Xcode

### 1. Create the Xcode project

1. Open Xcode → **File › New › Project**
2. Choose **iOS › App**
3. Settings:
   - Product Name: `QuizSolver`
   - Interface: `SwiftUI`
   - Language: `Swift`
   - Bundle Identifier: anything you own, e.g. `com.yourname.quizsolver`
4. Save into the `ios/` directory

### 2. Add the source files

Drag all `.swift` files from `ios/QuizSolver/` into the Xcode project navigator, making sure **Copy items if needed** is checked:

```
ios/QuizSolver/
├── QuizSolverApp.swift
├── ContentView.swift
├── Models/
│   └── QuizModels.swift
├── Services/
│   ├── OCRService.swift
│   ├── ClaudeAPIClient.swift
│   ├── ScreenshotMonitor.swift
│   └── NotificationService.swift
└── Views/
    └── AnswerOverlayView.swift
```

### 3. Replace Info.plist

Replace the auto-generated `Info.plist` with the one in this repo, or manually add these keys in **Signing & Capabilities → Info**:

| Key | Value |
|-----|-------|
| `NSPhotoLibraryUsageDescription` | Quiz Solver behöver tillgång till fotobiblioteket för att läsa av skärmbilder du tar under quiz-spel. |
| `NSUserNotificationsUsageDescription` | Quiz Solver visar svaret som en notis ovanpå quiz-appen. |

### 4. Enable Time Sensitive Notifications

In **Signing & Capabilities**, add the **Time Sensitive Notifications** capability. This allows the notification banner to appear on top of any app even in Focus modes.

### 5. Get an Anthropic API key

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Paste it in the app's key field (tap the 🔑 icon)

### 6. Build and run on a real device

The photo library and notifications do not work in Simulator — run on a physical iPhone.

## Usage

1. Open QuizSolver alongside the quiz app (Split View or Slide Over)
2. Tap **Starta Quiz Solver**
3. Approve the screen recording prompt from iOS
4. Switch to the quiz app — answers appear automatically as notification banners

## Architecture

```
RPScreenRecorder (live frame stream ~60 fps)
        │  throttled to 1 frame/sec
        ▼
OCRService (Apple Vision on-device, ~100–300 ms)
        │  raw OCR text
        │  skip if same question as before
        ▼
ClaudeAPIClient → POST /v1/messages  (claude-haiku-4-5, ~300–700 ms)
        │  single digit 1–4
        ▼
NotificationService → UNUserNotificationCenter
        │  .timeSensitive banner
        ▼
Notification visible on top of quiz app ✅
```

## Files

| File | Purpose |
|------|---------|
| `Services/LiveScreenMonitor.swift` | ReplayKit capture + OCR + API pipeline |
| `Services/OCRService.swift` | On-device Vision OCR |
| `Services/ClaudeAPIClient.swift` | Anthropic API — `claude-haiku-4-5` |
| `Services/NotificationService.swift` | UNUserNotificationCenter answer banner |
| `QuizSolverApp.swift` | App entry point + AppDelegate |
| `ContentView.swift` | SwiftUI main UI |
| `Views/AnswerOverlayView.swift` | In-app floating answer bubble |

## Privacy

- OCR runs entirely on-device via Apple's Vision framework — no image data leaves the phone
- Only the extracted text is sent to the Anthropic API
- The API key is stored in `UserDefaults` (consider Keychain for production use)
- Screen recording requires explicit user approval via iOS system dialog
