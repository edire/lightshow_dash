from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.utils.jwt_utils import verify_access_token
from backend.utils.oauth_utils import check_authorized_user

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to verify JWT token and extract user info.
    Used for protecting admin endpoints.
    """
    token = credentials.credentials

    try:
        # Verify the JWT access token
        user_info = verify_access_token(token)

        email = user_info.get("email", "")
        name = user_info.get("name", "")

        # Check if user is still authorized
        if not check_authorized_user(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {email} is not authorized"
            )

        return {
            "email": email,
            "name": name,
            "picture": ""
        }

    except ValueError as e:
        # Invalid or expired token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
