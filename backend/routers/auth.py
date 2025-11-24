from fastapi import APIRouter, HTTPException, status, Response, Request
from pydantic import BaseModel
from typing import Optional
import os

from backend.utils.oauth_utils import (
    get_authorization_url,
    exchange_code_for_tokens,
    refresh_access_token,
    verify_id_token
)

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    user_email: str
    user_name: str
    user_picture: str = ""


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthCallbackRequest(BaseModel):
    code: str
    state: str


@router.get("/login")
async def initiate_login():
    """
    Initiate Google OAuth flow.
    Returns authorization URL and state for the client to redirect to.
    """
    try:
        auth_url, state = get_authorization_url()
        return {
            "authorization_url": auth_url,
            "state": state
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}"
        )


@router.post("/callback", response_model=TokenResponse)
async def handle_callback(callback_data: AuthCallbackRequest):
    """
    Handle OAuth callback and exchange code for tokens.
    """
    try:
        tokens = exchange_code_for_tokens(callback_data.code, callback_data.state)
        return TokenResponse(**tokens)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        tokens = refresh_access_token(refresh_data.refresh_token)
        return TokenResponse(**tokens)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint - client should clear tokens on their side.
    """
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(request: Request):
    """
    Get current user info from access token.
    Expects Authorization: Bearer <token> header.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        user_info = verify_id_token(token)
        return user_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
