
import reflex as rx
from google_auth_oauthlib.flow import Flow
import os
import requests


SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
GAUTH_SECRETS_FILE = os.getenv("GAUTH_SECRETS_FILE")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:3000/oauth-callback")


ALLOW_LIST = os.getenv("ALLOW_LIST", "").split(",")
ALLOW_LIST = [x.strip() for x in ALLOW_LIST]
def check_authorized_user(email: str) -> bool:
    return email in ALLOW_LIST or '*@' + email.split('@')[1] in ALLOW_LIST


class AuthState(rx.State):
    user_email: str = ""
    user_name: str = ""
    is_authenticated: bool = False
    error_message: str = ""
    oauth_state: str = ""
    processing: bool = False
    checking_auth: bool = True
    refresh_token: str = rx.LocalStorage()
    access_token: str = ""
    stored_email: str = rx.LocalStorage()


    def check_auth(self):
        if not self.is_authenticated:
            if self.refresh_token and self.stored_email:
                if self.restore_session(self.refresh_token, self.stored_email):
                    self.checking_auth = False
                    return
            self.checking_auth = False
            return rx.redirect("/login")
        else:
            self.checking_auth = False


    def restore_session(self, refresh_token: str, email: str) -> bool:
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google.auth import exceptions as google_exceptions
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self._get_client_element('client_id'),
                client_secret=self._get_client_element('client_secret')
            )
            credentials.refresh(Request())
            userinfo_endpoint = 'https://www.googleapis.com/oauth2/v2/userinfo'
            headers = {'Authorization': f'Bearer {credentials.token}'}
            response = requests.get(userinfo_endpoint, headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                restored_email = user_info.get('email', '')
                if restored_email == email and check_authorized_user(restored_email):
                    self.user_email = restored_email
                    self.user_name = user_info.get('name', '')
                    self.is_authenticated = True
                    self.refresh_token = refresh_token
                    self.access_token = credentials.token
                    print(f"Session restored successfully for {restored_email}")
                    return True
                else:
                    print(f"User {restored_email} is no longer authorized")
                    self._clear_auth_tokens()
                    return False
            else:
                print(f"Failed to retrieve user info: HTTP {response.status_code}")
                self._clear_auth_tokens()
                return False
        except google_exceptions.RefreshError as e:
            print(f"Refresh token expired or revoked: {e}")
            self.error_message = "Your session has expired. Please sign in again."
            self._clear_auth_tokens()
            return False
        except requests.exceptions.RequestException as e:
            print(f"Network error during session restoration: {e}")
            self.error_message = "Network error. Please check your connection and try again."
            return False
        except Exception as e:
            print(f"Unexpected error during session restoration: {e}")
            self.error_message = "Failed to restore session. Please sign in again."
            self._clear_auth_tokens()
            return False


    def _clear_auth_tokens(self):
        self.refresh_token = ""
        self.stored_email = ""
        self.access_token = ""
        self.user_email = ""
        self.user_name = ""
        self.is_authenticated = False
        print("Authentication tokens cleared")


    def _get_client_element(self, element: str) -> str:
        try:
            import json
            with open(GAUTH_SECRETS_FILE, 'r') as f:
                secrets = json.load(f)
                return secrets['web'][element]
        except Exception as e:
            print(f"Error reading client element {element}: {e}")
            return ""


    def start_oauth_flow(self):
        self.error_message = ""
        try:
            flow = Flow.from_client_secrets_file(
                GAUTH_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='false',
                prompt='consent'  # Force re-consent to avoid scope mismatch issues
            )
            self.oauth_state = state
            return rx.redirect(authorization_url)
        except Exception as e:
            self.error_message = f"OAuth initialization failed: {str(e)}"
            print(f"Error in start_oauth_flow: {e}")
            return None


    def on_callback_load(self):
        try:
            from urllib.parse import urlparse, parse_qs
            url = str(self.router.url)
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            code = params.get("code", [""])[0]
            state = params.get("state", [""])[0]
            if code and state:
                self.processing = True
                return self.handle_oauth_callback(code, state)
            else:
                self.error_message = "Missing OAuth parameters"
                return rx.redirect("/login")
        except Exception as e:
            print(f"Error accessing query params: {e}")
            self.error_message = "Failed to process OAuth callback"
            return rx.redirect("/login")


    def handle_oauth_callback(self, code: str, state: str):
        try:
            # Verify state to prevent CSRF attacks
            if state != self.oauth_state:
                self.error_message = "Invalid OAuth state. Please try again."
                print(f"State mismatch: expected {self.oauth_state}, got {state}")
                self.processing = False
                return rx.redirect("/login")
            
            # Exchange the authorization code for credentials
            flow = Flow.from_client_secrets_file(
                GAUTH_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI,
                state=state
            )
            flow.fetch_token(code=code)
            credentials = flow.credentials

            # Get user info from Google
            userinfo_endpoint = 'https://www.googleapis.com/oauth2/v2/userinfo'
            headers = {'Authorization': f'Bearer {credentials.token}'}
            response = requests.get(userinfo_endpoint, headers=headers)

            if response.status_code == 200:
                user_info = response.json()
                email = user_info.get('email', '')
                name = user_info.get('name', '')

                # Check if email is in ALLOW_LIST
                if check_authorized_user(email):
                    self.user_email = email
                    self.user_name = name
                    self.is_authenticated = True
                    self.error_message = ""
                    self.processing = False

                    # Store tokens for persistent authentication
                    self.access_token = credentials.token
                    if credentials.refresh_token:
                        # Store refresh token in LocalStorage (persists across sessions)
                        self.refresh_token = credentials.refresh_token
                        self.stored_email = email
                        print(f"Stored refresh token for {email}")
                    else:
                        print("Warning: No refresh token received. User will need to re-authenticate.")

                    # Reset checking_auth for clean page load
                    self.checking_auth = False
                    return rx.redirect("/")
                else:
                    self.error_message = f"Access denied. Email '{email}' is not authorized."
                    self.is_authenticated = False
                    self.processing = False
                    return rx.redirect("/login")
            else:
                self.error_message = "Failed to retrieve user information."
                self.processing = False
                return rx.redirect("/login")

        except Exception as e:
            self.error_message = f"Authentication failed: {str(e)}"
            print(f"Error in handle_oauth_callback: {e}")
            self.processing = False
            return rx.redirect("/login")


    def logout(self):
        self._clear_auth_tokens()
        self.error_message = ""
        self.oauth_state = ""
        self.checking_auth = True
        print("User logged out")
        return rx.redirect("/login")


def require_auth(page_fn):
    def wrapped_page() -> rx.Component:
        return rx.cond(
            AuthState.checking_auth | ~AuthState.is_authenticated,
            rx.container(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Loading...", size="3"),
                    spacing="4",
                    justify="center",
                    align="center",
                    min_height="100vh",
                ),
                size="2",
            ),
            page_fn(),
        )
    wrapped_page._requires_auth = True
    wrapped_page.__name__ = page_fn.__name__
    wrapped_page.__doc__ = page_fn.__doc__
    return wrapped_page


@rx.page(route="/oauth-callback", on_load=[AuthState.on_callback_load])
def oauth_callback_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Completing authentication..."),
            rx.text("Please wait while we verify your credentials.", size="1", color="gray"),
            spacing="4",
            justify="center",
            align="center",
            min_height="100vh",
        ),
        size="2",
    )