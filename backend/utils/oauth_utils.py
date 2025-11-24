from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth import exceptions as google_exceptions
import os
import requests
import json

# OAuth configuration
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Load client secrets from volume directory
GAUTH_SECRETS_FILE = os.getenv('GAUTH_SECRETS_FILE')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost/oauth-callback')

try:
    with open(GAUTH_SECRETS_FILE) as f:
        CLIENT_SECRETS = json.load(f)
        WEB_CLIENT_ID = CLIENT_SECRETS['web']['client_id']
        WEB_CLIENT_SECRET = CLIENT_SECRETS['web']['client_secret']
except Exception as e:
    print(f"Error loading client secrets: {e}")
    CLIENT_SECRETS = {}
    WEB_CLIENT_ID = ""
    WEB_CLIENT_SECRET = ""

ALLOWED_EMAILS = os.getenv("ALLOW_LIST", "").split(",")
ALLOWED_EMAILS = [email.strip() for email in ALLOWED_EMAILS if email.strip()]


def check_authorized_user(email: str) -> bool:
    """Check if user email is in the allow list."""
    if not ALLOWED_EMAILS:
        print("[AUTH] Warning: ALLOW_LIST is empty, allowing all users")
        return True
    return email in ALLOWED_EMAILS


def create_oauth_flow():
    """Create and return a new OAuth flow instance."""
    return Flow.from_client_secrets_file(
        GAUTH_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )


def get_authorization_url() -> tuple[str, str]:
    """
    Generate OAuth authorization URL and state.
    Returns: (authorization_url, state)
    """
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url, state


def exchange_code_for_tokens(code: str, state: str) -> dict:
    """
    Exchange authorization code for access and refresh tokens.
    Returns dict with: access_token, refresh_token, user_email, user_name
    Raises: Exception on failure
    """
    try:
        flow = create_oauth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info
        userinfo_endpoint = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {credentials.token}'}
        response = requests.get(userinfo_endpoint, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.status_code}")
        
        user_info = response.json()
        email = user_info.get('email', '')
        
        # Check authorization
        if not check_authorized_user(email):
            raise Exception(f"User {email} is not authorized")
        
        return {
            'access_token': credentials.id_token if hasattr(credentials, 'id_token') and credentials.id_token else credentials.token,
            'refresh_token': credentials.refresh_token,
            'user_email': email,
            'user_name': user_info.get('name', ''),
            'user_picture': user_info.get('picture', '')
        }
        
    except Exception as e:
        print(f"[AUTH] Error exchanging code for tokens: {e}")
        raise


def refresh_access_token(refresh_token: str) -> dict:
    """
    Refresh access token using refresh token.
    Returns dict with: access_token, user_email, user_name
    Raises: Exception on failure
    """
    try:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=WEB_CLIENT_ID,
            client_secret=WEB_CLIENT_SECRET
        )
        
        request = Request()
        credentials.refresh(request)
        
        # Verify user info with the refreshed access token
        userinfo_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {credentials.token}'}
        response = requests.get(userinfo_endpoint, headers=headers)
        
        if response.status_code != 200:
            print(f"[AUTH] Error refreshing token: Failed to get user info: {response.status_code}")
            raise Exception(f"Failed to get user info: {response.status_code}")
        
        user_info = response.json()
        email = user_info.get('email', '')
        
        # Check authorization
        if not check_authorized_user(email):
            raise Exception(f"User {email} is no longer authorized")
        
        # Return the id_token if available, otherwise use access_token
        # The frontend uses this token for Bearer auth
        return {
            'access_token': credentials.id_token if hasattr(credentials, 'id_token') and credentials.id_token else credentials.token,
            'user_email': email,
            'user_name': user_info.get('name', ''),
            'user_picture': user_info.get('picture', '')
        }
        
    except google_exceptions.RefreshError as e:
        print(f"[AUTH] Refresh token expired or revoked: {e}")
        raise Exception("Session expired. Please sign in again.")
    except Exception as e:
        print(f"[AUTH] Error refreshing token: {e}")
        raise


def verify_id_token(token: str) -> dict:
    """
    Verify ID token and return user info.
    Returns dict with: email, name, picture
    Raises: ValueError on invalid token
    """
    idinfo = id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        WEB_CLIENT_ID
    )
    
    email = idinfo.get('email', '')
    if not check_authorized_user(email):
        raise ValueError(f"User {email} is not authorized")
    
    return {
        'email': email,
        'name': idinfo.get('name', ''),
        'picture': idinfo.get('picture', '')
    }
