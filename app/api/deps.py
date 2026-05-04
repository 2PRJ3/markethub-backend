from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session


from app.db.session import SessionLocal
from app.services.user_service import UserService
from app.core.security import decode_token
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.services.user_service import UserService
from app.utils.enums import UserRole


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def extract_token(request: Request) -> Optional[str]:
    token = request.cookies.get(settings.ACCES_COOKIE_NAME)

    if token:
        return token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1]

    return None

def get_current_user(request: Request, service: UserService = Depends(get_user_service)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Non authentifié"
    )
    token = extract_token(request)

    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception

        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception
        user_id_int = int(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    try:
        user = service.get_by_id(user_id_int)
    except NotFoundError:
        raise credentials_exception

    if user.is_suspended or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est supsendu. Veuillez contacter le support technique"
        )
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit"
        )
    return current_user