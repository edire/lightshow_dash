import jwt
import os
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 60


def create_access_token(email: str, name: str) -> str:
    """
    Create a JWT access token.
    - Expires in 15 minutes
    - Contains: sub (email), name, exp
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": email,
        "name": name,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> Optional[Dict[str, str]]:
    """
    Verify and decode JWT access token.
    Returns: {"sub": email, "name": name} or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "email": payload.get("sub"),
            "name": payload.get("name")
        }
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def generate_refresh_token() -> str:
    """
    Generate a secure random refresh token.
    Returns: 64-character hex string
    """
    return secrets.token_hex(32)


def hash_refresh_token(token: str) -> str:
    """
    Hash refresh token using bcrypt.
    Returns: bcrypt hash string
    """
    return bcrypt.hashpw(token.encode(), bcrypt.gensalt()).decode()


def verify_refresh_token_hash(token: str, token_hash: str) -> bool:
    """
    Verify refresh token against its hash.
    Returns: True if valid, False otherwise
    """
    try:
        return bcrypt.checkpw(token.encode(), token_hash.encode())
    except Exception:
        return False


def get_refresh_token_expiry_seconds() -> int:
    """Get refresh token expiry in seconds (60 days)."""
    return REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
