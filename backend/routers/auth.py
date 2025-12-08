from fastapi import APIRouter, HTTPException, status, Response, Request, Cookie
from pydantic import BaseModel
from typing import Optional
import os

from backend.utils.oauth_utils import (
    get_authorization_url,
    exchange_code_for_tokens_google,
    check_authorized_user
)
from backend.utils.jwt_utils import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_refresh_token_hash,
    get_refresh_token_expiry_seconds
)
from backend.utils.redis_client import (
    store_refresh_token,
    get_refresh_token_data,
    revoke_refresh_token,
    revoke_all_user_tokens,
    is_token_revoked,
    mark_token_as_revoked
)

router = APIRouter()

IS_DEV = os.getenv("IS_DEV", "0") == "1"

# Cookie settings
COOKIE_NAME = "refresh_token"
COOKIE_MAX_AGE = 60 * 24 * 60 * 60  # 60 days in seconds
COOKIE_PATH = "/api/auth"
COOKIE_SECURE = not IS_DEV  # True in production, False in dev
COOKIE_HTTPONLY = True
COOKIE_SAMESITE = "lax"


class TokenResponse(BaseModel):
    access_token: str
    user: dict


class UserResponse(BaseModel):
    email: str
    name: str
    picture: str = ""


@router.get("/login-url")
async def get_login_url():
    """
    Get Google OAuth login URL.
    Returns authorization URL for client to redirect to.
    """
    try:
        auth_url, _ = get_authorization_url()
        return {"url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate login URL: {str(e)}"
        )


@router.get("/callback")
async def handle_callback(code: str, response: Response):
    """
    Handle OAuth callback and exchange code for tokens.
    - Exchanges code for Google tokens
    - Verifies email against allowlist
    - Creates JWT access token (15 min)
    - Generates refresh token (60 days)
    - Sets HttpOnly cookie with refresh token
    - Returns access token to client
    """
    try:
        # Exchange code for Google tokens and get user info
        user_info = exchange_code_for_tokens_google(code)
        email = user_info["email"]
        name = user_info["name"]
        picture = user_info.get("picture", "")

        # Check authorization
        if not check_authorized_user(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {email} is not authorized"
            )

        # Create JWT access token
        access_token = create_access_token(email, name)

        # Generate refresh token
        refresh_token = generate_refresh_token()

        # Hash with SHA256 for Redis key (fast lookup)
        import hashlib
        token_key = hashlib.sha256(refresh_token.encode()).hexdigest()

        # Store refresh token in Redis
        store_refresh_token(
            token_hash=token_key,
            user_email=email,
            expires_in_seconds=get_refresh_token_expiry_seconds()
        )

        # Set HttpOnly cookie with refresh token
        response.set_cookie(
            key=COOKIE_NAME,
            value=refresh_token,
            max_age=COOKIE_MAX_AGE,
            path=COOKIE_PATH,
            secure=COOKIE_SECURE,
            httponly=COOKIE_HTTPONLY,
            samesite=COOKIE_SAMESITE
        )

        return TokenResponse(
            access_token=access_token,
            user={
                "email": email,
                "name": name,
                "picture": picture
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH] Callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token")
):
    """
    Refresh access token using refresh token from cookie.
    - Validates refresh token from database
    - Implements token rotation (invalidates old token)
    - Detects token reuse (security breach)
    - Creates new access token
    - Creates new refresh token
    - Sets new HttpOnly cookie
    - Returns new access token
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    try:
        # Hash the token to look it up in Redis
        # Note: We need to iterate through stored hashes to find a match
        # This is a limitation of bcrypt - we can't hash and lookup directly
        # In a production system, you might want to use a different approach
        # For now, we'll store the token hash as the key itself

        # Actually, let's change the approach: store the raw token as key (hashed with SHA256)
        # and the data as value. This is more efficient for lookup.
        # Let me update redis_client.py approach

        # For now, let's use SHA256 for the Redis key (fast lookup)
        # and verify with bcrypt if needed (though we trust Redis)
        import hashlib
        token_key = hashlib.sha256(refresh_token.encode()).hexdigest()

        token_data = get_refresh_token_data(token_key)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Check if token was revoked (reuse detection)
        if is_token_revoked(token_key):
            # Token reuse detected! Revoke all user tokens
            user_email = token_data.get("user_email")
            if user_email:
                print(f"[AUTH] Token reuse detected for {user_email}! Revoking all tokens.")
                revoke_all_user_tokens(user_email)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token reuse detected. All sessions invalidated. Please sign in again."
            )

        user_email = token_data.get("user_email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data"
            )

        # Check if user is still authorized
        if not check_authorized_user(user_email):
            revoke_refresh_token(token_key)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {user_email} is no longer authorized"
            )

        # Invalidate old refresh token (rotation)
        revoke_refresh_token(token_key)

        # Create new access token
        # We don't have the user's name stored, so we'll use email
        # In a real system, you'd store this in Redis or fetch from DB
        access_token = create_access_token(user_email, user_email.split("@")[0])

        # Generate new refresh token
        new_refresh_token = generate_refresh_token()
        new_token_key = hashlib.sha256(new_refresh_token.encode()).hexdigest()

        # Store new refresh token in Redis
        store_refresh_token(
            token_hash=new_token_key,
            user_email=user_email,
            expires_in_seconds=get_refresh_token_expiry_seconds()
        )

        # Set new HttpOnly cookie
        response.set_cookie(
            key=COOKIE_NAME,
            value=new_refresh_token,
            max_age=COOKIE_MAX_AGE,
            path=COOKIE_PATH,
            secure=COOKIE_SECURE,
            httponly=COOKIE_HTTPONLY,
            samesite=COOKIE_SAMESITE
        )

        return {"access_token": access_token}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH] Refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        )


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token")
):
    """
    Logout user.
    - Invalidates refresh token in database
    - Clears HttpOnly cookie
    """
    if refresh_token:
        try:
            import hashlib
            token_key = hashlib.sha256(refresh_token.encode()).hexdigest()
            revoke_refresh_token(token_key)
        except Exception as e:
            print(f"[AUTH] Logout error: {e}")

    # Clear cookie
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH
    )

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(request: Request):
    """
    Get current user info from access token.
    Expects Authorization: Bearer <token> header.

    This endpoint requires the JWT token to be verified by the
    get_current_user dependency, which should be applied at the router level
    or by the caller.
    """
    # This will be handled by the dependency in the route that uses this
    # For now, we'll extract from the header directly
    from backend.utils.jwt_utils import verify_access_token

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.split(" ")[1]

    try:
        user_info = verify_access_token(token)
        return {
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": ""  # We don't store picture in JWT, could fetch from Google if needed
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
