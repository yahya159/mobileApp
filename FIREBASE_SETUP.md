# Firebase Authentication Setup Guide

This guide will help you set up Firebase Authentication for the EMSI Chatbot mobile app.

## Quick Start: Using FlutterFire CLI (Recommended)

If you have Firebase CLI installed, you can use FlutterFire CLI to automatically configure Firebase:

```bash
# Install FlutterFire CLI (if not already installed)
dart pub global activate flutterfire_cli

# Add to PATH (Windows PowerShell - for current session)
$env:Path += ";C:\Users\$env:USERNAME\AppData\Local\Pub\Cache\bin"

# Login to Firebase (will open browser)
firebase login

# Configure Firebase for your project
cd mobile_app
flutterfire configure --project=YOUR_PROJECT_ID
```

This will automatically:
- Download `google-services.json` for Android
- Create `lib/firebase_options.dart` for Flutter
- Configure Firebase for all platforms

**Note**: If you use FlutterFire CLI, you may need to update `lib/main.dart` to use `firebase_options.dart`:
```dart
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}
```

## Manual Setup (Alternative)

If you prefer manual setup or FlutterFire CLI doesn't work, follow the steps below.

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project (e.g., `emsiapp-d9641`)
3. Follow the setup wizard:
   - Enter project name (e.g., "EMSI Chatbot")
   - Enable/disable Google Analytics (optional)
   - Click "Create project"

## Step 2: Enable Authentication

1. In Firebase Console, go to **Authentication** > **Get started**
2. Click on **Sign-in method** tab
3. Enable the following providers:
   - **Email/Password**: Click, enable, and save
   - **Google**: Click, enable, and configure:
     - Add your project's support email
     - Add authorized domains if needed
     - Save

## Step 3: Register Android App

1. In Firebase Console, click the **Android** icon (or go to Project Settings > Your apps)
2. Register your Android app:
   - **Package name**: `com.emsi.chatbot` (must match `mobile_app/android/app/build.gradle` line 45: `applicationId "com.emsi.chatbot"`)
   - **App nickname**: EMSI Chatbot (optional)
   - **Debug signing certificate SHA-1**: Optional for now (needed for Google Sign-In)
3. Click "Register app"
4. Download `google-services.json`
5. Place the file in: `mobile_app/android/app/google-services.json`

**Important**: The Google Services plugin is already configured in:
- `mobile_app/android/build.gradle` (line 10: Google Services classpath)
- `mobile_app/android/app/build.gradle` (line 5: Google Services plugin applied)

The app will automatically use this file when you build.

## Step 4: Register Web App (for Windows/Web support)

1. In Firebase Console, click the **Web** icon (</>) 
2. Register your web app:
   - **App nickname**: EMSI Chatbot Web
   - **Firebase Hosting**: Not needed for now
3. Click "Register app"
4. Copy the Firebase configuration object (it looks like this):
   ```javascript
   const firebaseConfig = {
     apiKey: "AIza...",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-project-id",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123"
   };
   ```
5. Update `mobile_app/web/index.html` (lines 43-50):
   - Replace the placeholder values in the `firebaseConfig` object (lines 44-49) with your actual values from Firebase Console
   - The Firebase SDK scripts are already included (lines 36-37)
   - Firebase initialization is already set up (line 53)

## Step 5: Get Firebase Admin SDK Service Account

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Go to **Service accounts** tab
3. Click **Generate new private key**
4. Click "Generate key" in the dialog
5. A JSON file will be downloaded
6. Save this file as `api_server_service_account.json` in the project root (same directory as `api_server.py`)

**Important**: Never commit this file to version control! It's already in `.gitignore`.

## Step 6: Configure Google Sign-In (Optional but Recommended)

### For Android:
1. In Firebase Console, go to **Authentication** > **Sign-in method** > **Google**
2. Note your **Web client ID** (you'll need this)
3. In [Google Cloud Console](https://console.cloud.google.com/):
   - Select your Firebase project
   - Go to **APIs & Services** > **Credentials**
   - Find your OAuth 2.0 Client ID for Android
   - If it doesn't exist, create one:
     - Click "Create Credentials" > "OAuth client ID"
     - Application type: Android
     - Package name: `com.emsi.chatbot`
     - SHA-1: Get from `keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android`

### For Web:
1. In Google Cloud Console, create an OAuth 2.0 Client ID for Web application
2. Add authorized JavaScript origins:
   - `http://localhost` (for development)
   - Your production domain (when deployed)

## Step 7: Install Dependencies

### Python (API Server):
```bash
# Activate virtual environment first (if using one)
# On Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

This will install:
- `firebase-admin>=6.4.0` (for API server token verification)
- All other required dependencies

### Flutter (Mobile App):
```bash
cd mobile_app
flutter pub get
```

This will install:
- `firebase_core: ^2.24.2`
- `firebase_auth: ^4.15.3`
- `google_sign_in: ^6.1.6`
- `firebase_auth_web: ^5.0.3`
- All other dependencies from `pubspec.yaml`

## Step 8: Verify Firebase Initialization

The Flutter app is already configured to initialize Firebase on startup. Check `mobile_app/lib/main.dart`:

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();  // Firebase initialization
  runApp(const MyApp());
}
```

The app uses an `AuthWrapper` that:
- Shows `LoginScreen` if user is not authenticated
- Shows `ChatScreen` if user is authenticated
- Automatically handles auth state changes

## Step 9: Test the Setup

1. Start the API server:
   ```bash
   # From project root
   python api_server.py
   ```
   You should see: `✅ Firebase Admin SDK initialized`
   
   If you see a warning instead, make sure `api_server_service_account.json` is in the project root.

2. Run the Flutter app:
   ```bash
   cd mobile_app
   flutter run -d windows  # For Windows desktop
   # or
   flutter run -d chrome  # For web browser
   # or
   flutter run -d android # For Android device/emulator
   ```

3. Test authentication flow:
   - **Login Screen**: You should see the login screen first
   - **Sign Up**: Try creating an account with email/password
   - **Sign In**: Try signing in with existing credentials
   - **Google Sign-In**: Try signing in with Google (if configured)
   - **Password Reset**: Test "Forgot Password?" functionality
   - **Chat**: After signing in, you should see the chat screen
   - **Settings**: Go to Settings to see your account info and logout option
   - **API Calls**: Send a chat message - it should work with authentication token

## Troubleshooting

### "Firebase Admin SDK not initialized"
- Make sure `api_server_service_account.json` is in the project root
- Check that the file is valid JSON
- Verify the service account has proper permissions

### "google-services.json not found"
- Make sure the file is in `mobile_app/android/app/`
- Verify the package name matches: `com.emsi.chatbot`

### "Google Sign-In not working"
- Check that Google Sign-In is enabled in Firebase Console
- Verify OAuth client IDs are configured correctly
- For Android: Check SHA-1 certificate fingerprint
- For Web: Check authorized domains

### "Authentication required" error
- Make sure you're signed in to the app (check if you see LoginScreen)
- Check that the API server has Firebase Admin SDK initialized
- Verify the token is being sent in the Authorization header
- Check `mobile_app/lib/providers/chat_provider.dart` - `setAuthProvider()` should be called
- Verify `mobile_app/lib/services/api_service.dart` - `setTokenCallback()` is configured

### "App shows LoginScreen but I'm already signed in"
- Check Firebase Console > Authentication > Users to see if your user exists
- Try signing out and signing in again
- Check browser console (for web) or logs (for desktop) for Firebase errors

### "Firebase.initializeApp() error"
- For Web: Make sure `web/index.html` has the correct Firebase config
- For Android: Verify `google-services.json` is in `android/app/`
- Check that all Firebase dependencies are installed: `flutter pub get`
- Verify your Firebase project is active in Firebase Console

## Security Notes

1. **Never commit** `api_server_service_account.json` to version control
2. **Never commit** `google-services.json` if it contains sensitive data (it's usually safe, but be cautious)
3. Use environment variables for production deployments
4. Restrict Firebase rules to only allow authenticated users
5. Regularly rotate service account keys

## App Structure

The authentication is integrated into the app as follows:

### Files Structure:
```
mobile_app/
├── lib/
│   ├── main.dart                    # Firebase initialization + AuthWrapper
│   ├── models/
│   │   └── user_model.dart         # User data model
│   ├── providers/
│   │   ├── auth_provider.dart      # Authentication state management
│   │   ├── chat_provider.dart      # Chat with auth token support
│   │   └── settings_provider.dart  # Settings management
│   ├── screens/
│   │   ├── login_screen.dart       # Login UI (email/password + Google)
│   │   ├── signup_screen.dart      # Sign up UI
│   │   ├── chat_screen.dart        # Main chat interface (protected)
│   │   └── settings_screen.dart    # Settings with logout
│   └── services/
│       └── api_service.dart        # API calls with auth tokens
├── android/
│   └── app/
│       └── google-services.json    # Firebase Android config
└── web/
    └── index.html                   # Firebase Web config
```

### Authentication Flow:
1. App starts → `main()` initializes Firebase
2. `AuthWrapper` checks auth state via `AuthProvider`
3. If not authenticated → Shows `LoginScreen`
4. User signs in → `AuthProvider` updates state
5. `AuthWrapper` detects change → Shows `ChatScreen`
6. API calls include Firebase ID token in Authorization header
7. API server verifies token using Firebase Admin SDK

### Protected Endpoints:
- `/api/chat` - Requires authentication
- `/api/chat/simple` - Requires authentication
- `/api/health` - Public (no auth required)
- `/api/status` - Public (no auth required)

## Next Steps

- Set up Firebase Security Rules for Firestore (if you plan to use it)
- Configure custom email templates in Firebase Console
- Set up password reset email templates
- Consider adding more authentication providers (Facebook, Apple, etc.)
- Add user profile management features
- Implement remember me / persistent login
- Add email verification requirement

