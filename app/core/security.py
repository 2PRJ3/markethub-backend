from typing import Optional

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_token(subject: int | str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(subject: int |str, expires_delta: Optional[timedelta] = None)->str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION)
    return create_token(subject, expires_delta, token_type="access")

def create_refresh_token(subject: int | str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRATION)
    return create_token(subject, expires_delta, token_type="refresh")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])