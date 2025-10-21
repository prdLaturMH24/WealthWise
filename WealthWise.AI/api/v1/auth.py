from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from middleware.auth_middleware import auth_manager, get_user_by_id
from datetime import datetime

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_on: datetime

class TokenRequest(BaseModel):
    username: str
    password: str

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: TokenRequest) -> TokenResponse:
    """
    JWT access token generation endpoint.
    You must POST username and password (form-encoded) to obtain a token.
    """
    # Replace this logic with your real authentication
    user = await get_user_by_id(form_data.username)
    if not user or form_data.password != "demo":  # Replace password logic in production!
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    auth_token = auth_manager.create_access_token(user_id=user["user_id"])
    return TokenResponse(access_token=auth_token.access_token, token_type="bearer", expires_on=auth_token.expires_on)