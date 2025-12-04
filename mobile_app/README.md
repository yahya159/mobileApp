# EMSI Chatbot Mobile App

Flutter mobile application for the EMSI Chatbot.

## Prerequisites

1. **Flutter SDK**: Install Flutter from [flutter.dev](https://flutter.dev/docs/get-started/install)
2. **Android Studio** or **VS Code** with Flutter extensions
3. **API Server**: The FastAPI server must be running (see main project README)

## Setup Instructions

### 1. Install Dependencies

```bash
cd mobile_app
flutter pub get
```

### 2. Configure API Server URL

For **Android Emulator**:
- The default URL `http://10.0.2.2:5000` should work (10.0.2.2 is the emulator's alias for localhost)

For **Physical Device**:
- Find your computer's IP address:
  - Windows: `ipconfig` (look for IPv4 address)
  - Mac/Linux: `ifconfig` or `ip addr`
- Update the API URL in `lib/services/api_service.dart` or use the Settings screen in the app

### 3. Start the API Server

Before running the mobile app, make sure the FastAPI server is running:

```bash
# From the project root
python api_server.py
```

The API server should be accessible at `http://localhost:5000`

### 4. Run the App

```bash
# For Android
flutter run

# For iOS (Mac only)
flutter run -d ios

# For a specific device
flutter devices  # List available devices
flutter run -d <device-id>
```

## Building for Release

### Android APK

```bash
flutter build apk --release
```

The APK will be in `build/app/outputs/flutter-apk/app-release.apk`

### Android App Bundle (for Play Store)

```bash
flutter build appbundle --release
```

### iOS (Mac only)

```bash
flutter build ios --release
```

## Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── models/
│   │   └── message.dart          # Message model
│   ├── providers/
│   │   ├── chat_provider.dart    # Chat state management
│   │   └── settings_provider.dart # Settings state management
│   ├── screens/
│   │   ├── chat_screen.dart      # Main chat interface
│   │   └── settings_screen.dart  # Settings screen
│   └── services/
│       └── api_service.dart      # API communication
├── pubspec.yaml                  # Flutter dependencies
└── README.md                     # This file
```

## Features

- 💬 Real-time chat interface
- 🔄 Streaming responses from the API
- 📚 RAG (Retrieval-Augmented Generation) support
- ⚙️ Configurable model parameters
- 🌙 Dark mode support
- 📱 Responsive design

## Troubleshooting

### Connection Issues

1. **Android Emulator**: Make sure you're using `http://10.0.2.2:5000` (not localhost)
2. **Physical Device**: 
   - Ensure your phone and computer are on the same WiFi network
   - Use your computer's IP address (e.g., `http://192.168.1.100:5000`)
   - Make sure the firewall allows connections on port 5000

### API Server Not Responding

- Check that `api_server.py` is running
- Verify Ollama is running: `ollama serve`
- Check API server logs for errors

### Build Issues

- Run `flutter clean` and `flutter pub get`
- Make sure you have the latest Flutter SDK
- Check that all dependencies in `pubspec.yaml` are compatible

## Development

### Adding New Features

1. Create models in `lib/models/`
2. Add API endpoints in `lib/services/api_service.dart`
3. Update providers for state management
4. Create new screens in `lib/screens/`

### Testing

```bash
flutter test
```

## License

Same as the main project.

