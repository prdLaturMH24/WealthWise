"""
Authentication and Authorization Middleware
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthManager:
    """Manages authentication and authorization"""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours

    def create_access_token(self, user_id: str, additional_data: Optional[Dict] = None) -> str:
        """Create JWT access token"""
        try:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

            payload = {
                "user_id": user_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            }

            if additional_data:
                payload.update(additional_data)

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token

        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )

    def verify_token(self, token: str) -> Dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token"
            )

auth_manager = AuthManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Dependency to get current authenticated user

    For demo purposes, this returns a mock user.
    In production, integrate with your authentication system.
    """
    try:
        # For demo, return mock user - replace with real authentication
        if settings.debug:
            return {
                "user_id": "demo_user_123",
                "email": "demo@example.com",
                "subscription_plan": "premium",
                "permissions": ["financial_advice", "recommendations", "goal_planning"]
            }

        # Production authentication
        token = credentials.credentials
        payload = auth_manager.verify_token(token)

        # Get user details from database or external service
        user_data = await get_user_by_id(payload["user_id"])

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Get user details by ID (implement with your user storage)
    """
    # This is a placeholder - implement with your user database
    mock_users = {
        "demo_user_123": {
            "user_id": "demo_user_123",
            "email": "demo@example.com",
            "subscription_plan": "premium",
            "permissions": ["financial_advice", "recommendations", "goal_planning"],
            "rate_limit_tier": "premium"
        }
    }

    return mock_users.get(user_id)

async def require_permission(permission: str):
    """Dependency to require specific permission"""
    async def permission_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        if permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user

    return permission_checker
