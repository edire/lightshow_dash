from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

security = HTTPBearer()

# OAuth configuration
import json

# OAuth configuration
GAUTH_SECRETS_FILE = os.getenv('GAUTH_SECRETS_FILE')
try:
    with open(GAUTH_SECRETS_FILE) as f:
        CLIENT_SECRETS = json.load(f)
        WEB_CLIENT_ID = CLIENT_SECRETS['web']['client_id']
except Exception as e:
    print(f"Error loading client secrets in dependencies: {e}")
    WEB_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
ALLOWED_EMAILS = os.getenv("ALLOW_LIST", "").split(",")
ALLOWED_EMAILS = [email.strip() for email in ALLOWED_EMAILS if email.strip()]


def check_authorized_user(email: str) -> bool:
    """Check if user email is in the allow list."""
    if not ALLOWED_EMAILS:
        print("[AUTH] Warning: ALLOW_LIST is empty, allowing all users")
        return True
    return email in ALLOWED_EMAILS


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to verify JWT token and extract user info.
    Used for protecting admin endpoints.
    """
    token = credentials.credentials
    
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            WEB_CLIENT_ID
        )
        
        email = idinfo.get("email", "")
        
        # Check if user is authorized
        if not check_authorized_user(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {email} is not authorized"
            )
        
        return {
            "email": email,
            "name": idinfo.get("name", ""),
            "picture": idinfo.get("picture", "")
        }
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
