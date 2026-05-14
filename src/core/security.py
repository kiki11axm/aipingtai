from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from jose import JWTError, jwt
from src.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class TokenData(BaseModel):
    username: str
    user_id: str
    user_type: str
    organization_id: Optional[str] = None


class User(BaseModel):
    id: str
    username: str
    user_type: str
    organization_id: Optional[str] = None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        user_type: str = payload.get("user_type")
        if username is None:
            raise credentials_exception
        return TokenData(
            username=username,
            user_id=user_id,
            user_type=user_type
        )
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    if current_user.user_type not in ["FARMER", "ADMIN", "MONITOR", "CARBON_ADMIN"]:
        raise HTTPException(status_code=400, detail="无效的用户类型")
    return current_user


def require_permissions(*permissions: str):
    async def permission_checker(
        current_user: TokenData = Depends(get_current_user)
    ) -> TokenData:
        return current_user
    return permission_checker
