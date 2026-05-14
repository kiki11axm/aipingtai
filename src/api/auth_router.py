from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger

from src.core.config import settings
from src.core.security import TokenData
from pydantic import BaseModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    user_type: str = "FARMER"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    demo_users = {
        "admin": {"password": "admin123", "user_id": "1", "user_type": "ADMIN"},
        "farmer": {"password": "farmer123", "user_id": "2", "user_type": "FARMER"},
        "monitor": {"password": "monitor123", "user_id": "3", "user_type": "MONITOR"},
        "carbon_admin": {"password": "carbon123", "user_id": "4", "user_type": "CARBON_ADMIN"}
    }

    user = demo_users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token({
        "sub": form_data.username,
        "user_id": user["user_id"],
        "user_type": user["user_type"]
    })
    refresh_token = create_refresh_token({
        "sub": form_data.username,
        "user_id": user["user_id"]
    })

    logger.info(f"用户登录成功: {form_data.username}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/register")
async def register(user_data: UserCreate):
    return {
        "message": "用户注册成功",
        "username": user_data.username,
        "user_id": "new_user_id"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    new_access_token = create_access_token({"sub": username, "user_id": payload.get("user_id")})
    new_refresh_token = create_refresh_token({"sub": username, "user_id": payload.get("user_id")})

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me")
async def get_current_user_info(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        user_type: str = payload.get("user_type")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证令牌")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    return TokenData(
        username=username,
        user_id=user_id,
        user_type=user_type
    )


@router.post("/logout")
async def logout():
    return {"message": "登出成功"}


@router.get("/permissions")
async def get_user_permissions(token: str = Depends(oauth2_scheme)):
    return {
        "permissions": [
            "farm:plot:read",
            "farm:plot:write",
            "farm:operation:read",
            "farm:operation:write",
            "trace:batch:read",
            "trace:batch:write",
            "carbon:account:read",
            "carbon:account:write",
            "carbon:ledger:read",
            "carbon:ledger:write"
        ]
    }
