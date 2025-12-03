# Mobile App Setup Guide

Complete guide to set up and run the EMSI Chatbot mobile application.

## Prerequisites

1. **Flutter SDK**: 
   - Download from [flutter.dev](https://flutter.dev/docs/get-started/install)
   - Verify installation: `flutter doctor`

2. **Android Studio** or **VS Code**:
   - Android Studio: Install Flutter and Dart plugins
   - VS Code: Install Flutter extension

3. **API Server Running**:
   - The Flask API server (`api_server.py`) must be running
   - Ollama must be running (`ollama serve`)

## Step-by-Step Setup

### 1. Install Flutter Dependencies

```bash
cd mobile_app
flutter pub get
```

### 2. Configure API Server URL

#### For Android Emulator:
The default URL `http://10.0.2.2:5000` should work automatically. This is the emulator's special IP that maps to your computer's localhost.

#### For Physical Device:
1. Find your computer's IP address:
   - **Windows**: Open Command Prompt and run `ipconfig`
     - Look for "IPv4 Address" under your active network adapter
     - Example: `192.168.1.100`
   
   - **Mac/Linux**: Run `ifconfig` or `ip addr`
     - Look for `inet` address (usually starts with 192.168.x.x or 10.x.x.x)

2. Update the API URL:
   - Open the app and go to Settings
   - Enter: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.1.100:5000`

### 3. Start the API Server

**Important**: The API server must be running before using the mobile app.

```bash
# From project root
python api_server.py
```

You should see:
```
🚀 Starting EMSI Chatbot API Server...
📡 API will be available at http://localhost:5000
```

### 4. Start Ollama

In a separate terminal:

```bash
ollama serve
```

### 5. Run the Mobile App

#### Option A: Using Flutter CLI

```bash
cd mobile_app

# List available devices
flutter devices

# Run on connected device/emulator
flutter run

# Run on specific device
flutter run -d <device-id>
```

#### Option B: Using Android Studio

1. Open Android Studio
2. File → Open → Select `mobile_app` folder
3. Wait for Flutter to sync
4. Select a device from the device dropdown
5. Click Run (▶️)

#### Option C: Using VS Code

1. Open VS Code
2. File → Open Folder → Select `mobile_app` folder
3. Press `F5` or click Run → Start Debugging
4. Select a device when prompted

## Building for Release

### Android APK (for direct installation)

```bash
cd mobile_app
flutter build apk --release
```

APK location: `build/app/outputs/flutter-apk/app-release.apk`

### Android App Bundle (for Play Store)

```bash
cd mobile_app
flutter build appbundle --release
```

AAB location: `build/app/outputs/bundle/release/app-release.aab`

### iOS (Mac only)

```bash
cd mobile_app
flutter build ios --release
```

## Troubleshooting

### Issue: "Connection refused" or "Cannot connect to server"

**Solutions:**
1. Verify API server is running: Check terminal where you ran `python api_server.py`
2. Check API URL in Settings:
   - Emulator: Should be `http://10.0.2.2:5000`
   - Physical device: Should be `http://YOUR_COMPUTER_IP:5000`
3. Firewall: Ensure Windows Firewall allows connections on port 5000
4. Network: Ensure phone and computer are on the same WiFi network

### Issue: "Ollama is not running"

**Solutions:**
1. Start Ollama: `ollama serve`
2. Verify Ollama is accessible: Open browser to `http://localhost:11434/api/tags`
3. Check API server logs for connection errors

### Issue: Flutter build errors

**Solutions:**
1. Clean build: `flutter clean`
2. Get dependencies: `flutter pub get`
3. Update Flutter: `flutter upgrade`
4. Check Flutter doctor: `flutter doctor`

### Issue: App crashes on launch

**Solutions:**
1. Check device logs: `flutter logs`
2. Verify all dependencies in `pubspec.yaml` are compatible
3. Try running in debug mode: `flutter run --debug`
4. Check AndroidManifest.xml permissions

### Issue: Slow response or timeout

**Solutions:**
1. Check network connection
2. Verify API server is responding: Test with `curl http://localhost:5000/api/health`
3. Increase timeout in `api_service.dart` if needed
4. Check Ollama model is loaded and responding

## Testing the Connection

### Test API Server

```bash
# Health check
curl http://localhost:5000/api/health

# Status check
curl http://localhost:5000/api/status
```

### Test from Mobile App

1. Open the app
2. Go to Settings
3. Tap "Refresh Connection"
4. Check connection status indicator (green = connected, red = disconnected)

## Network Configuration

### Finding Your Computer's IP Address

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" - usually something like `192.168.1.xxx`

**Mac/Linux:**
```bash
ifconfig | grep "inet "
# or
ip addr show | grep "inet "
```

### Firewall Configuration

**Windows:**
1. Open Windows Defender Firewall
2. Advanced Settings → Inbound Rules
3. New Rule → Port → TCP → 5000
4. Allow the connection

**Mac:**
1. System Preferences → Security & Privacy → Firewall
2. Firewall Options → Add Python to allowed apps

## Development Tips

1. **Hot Reload**: Press `r` in terminal while app is running
2. **Hot Restart**: Press `R` in terminal
3. **View Logs**: `flutter logs` or check VS Code/Android Studio console
4. **Debug Mode**: Run with `flutter run --debug` for detailed logs

## Next Steps

- Customize the UI in `lib/screens/`
- Add new features in `lib/providers/`
- Modify API calls in `lib/services/api_service.dart`
- Update styling in `lib/main.dart` theme

## Support

For issues:
1. Check the main README.md
2. Review API server logs
3. Check Flutter logs: `flutter logs`
4. Verify all prerequisites are installed correctly

