"""
Firebase Authentication Middleware for FastAPI
"""
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth

from ...config import Settings

# Initialize Firebase Admin SDK
firebase_initialized = False
try:
    if Settings.FIREBASE_SERVICE_ACCOUNT_PATH.exists():
        cred = credentials.Certificate(str(Settings.FIREBASE_SERVICE_ACCOUNT_PATH))
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("✅ Firebase Admin SDK initialized")
    else:
        print("⚠️  Firebase service account file not found. Authentication will be disabled.")
        print(f"   Expected path: {Settings.FIREBASE_SERVICE_ACCOUNT_PATH}")
        print("   Please download service account JSON from Firebase Console and place it in config/")
except Exception as e:
    print(f"⚠️  Failed to initialize Firebase Admin SDK: {e}")
    print("   Authentication will be disabled. API endpoints will be accessible without authentication.")

# FastAPI security scheme
security = HTTPBearer(auto_error=False)


def verify_firebase_token(token: str) -> Optional[dict]:
    """Verify Firebase ID token and return decoded token"""
    if not firebase_initialized:
        return None
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    FastAPI dependency for Firebase authentication
    
    Returns:
        User info dict if authenticated, None if auth is disabled
    """
    if not firebase_initialized:
        # If Firebase is not initialized, allow access (for development)
        return None
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    try:
        # Extract token from "Bearer <token>"
        token = credentials.credentials
        decoded_token = verify_firebase_token(token)
        
        if not decoded_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        return {
            'uid': decoded_token.get('uid'),
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name'),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication error: {str(e)}"
        )


# Dependency that can be used in routes
RequireAuth = Depends(get_current_user)
