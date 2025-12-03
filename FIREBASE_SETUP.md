# Firebase Authentication Setup Guide

This guide will help you set up Firebase Authentication for the EMSI Chatbot mobile app.

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project
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
   - **Package name**: `com.emsi.chatbot` (must match `mobile_app/android/app/build.gradle`)
   - **App nickname**: EMSI Chatbot (optional)
   - **Debug signing certificate SHA-1**: Optional for now
3. Click "Register app"
4. Download `google-services.json`
5. Place the file in: `mobile_app/android/app/google-services.json`

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
5. Update `mobile_app/web/index.html`:
   - Replace the placeholder values in the `firebaseConfig` object with your actual values

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
pip install -r requirements.txt
```

### Flutter (Mobile App):
```bash
cd mobile_app
flutter pub get
```

## Step 8: Test the Setup

1. Start the API server:
   ```bash
   python api_server.py
   ```
   You should see: `✅ Firebase Admin SDK initialized`

2. Run the Flutter app:
   ```bash
   cd mobile_app
   flutter run
   ```

3. Test authentication:
   - Try signing up with email/password
   - Try signing in with Google
   - Send a chat message (should work with authentication)

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
- Make sure you're signed in to the app
- Check that the API server has Firebase Admin SDK initialized
- Verify the token is being sent in the Authorization header

## Security Notes

1. **Never commit** `api_server_service_account.json` to version control
2. **Never commit** `google-services.json` if it contains sensitive data (it's usually safe, but be cautious)
3. Use environment variables for production deployments
4. Restrict Firebase rules to only allow authenticated users
5. Regularly rotate service account keys

## Next Steps

- Set up Firebase Security Rules for Firestore (if you plan to use it)
- Configure custom email templates in Firebase Console
- Set up password reset email templates
- Consider adding more authentication providers (Facebook, Apple, etc.)

