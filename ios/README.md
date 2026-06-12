# QuizSolver – iPhone Quiz Assistant

Solves multiple-choice quiz questions in ~1 second using on-device OCR + Claude Haiku 4.5.

## How it works

1. You take a screenshot of the quiz question (Side button + Volume up)
2. The app detects the new screenshot via `PHPhotoLibraryChangeObserver`
3. Apple Vision extracts the text on-device (~100–300 ms)
4. Claude Haiku 4.5 identifies the correct answer (~300–700 ms)
5. The answer appears as a notification banner on top of the quiz app

**Total latency: ~600 ms – 1.4 s**

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

1. Open QuizSolver in Split View or Slide Over alongside the quiz app
2. Tap **Starta Quiz Solver**
3. Grant photo library access when prompted
4. When a question appears, take a screenshot (Side button + Volume up)
5. Within ~1 second, a notification banner shows the answer number

## Architecture

```
Screenshot taken by user
        │
        ▼
PHPhotoLibraryChangeObserver (ScreenshotMonitor)
        │  detects new PHAsset
        ▼
PHImageManager → UIImage
        │
        ▼
OCRService (Apple Vision on-device)
        │  raw OCR text
        ▼
ClaudeAPIClient → POST /v1/messages  (claude-haiku-4-5)
        │  single digit 1–4
        ▼
NotificationService → UNUserNotificationCenter
        │  .timeSensitive banner
        ▼
Notification visible on top of quiz app ✅
```

## Privacy

- OCR runs entirely on-device via Apple's Vision framework — no image data leaves the phone
- Only the extracted text is sent to the Anthropic API
- The API key is stored in `UserDefaults` (consider Keychain for production use)
