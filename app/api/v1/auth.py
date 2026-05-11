from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError

from app.api.deps import get_current_user, get_user_service
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.ACCES_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        max_age=settings.ACCESS_TOKEN_EXPIRATION * 60,
        path="/",
    )
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        max_age=settings.REFRESH_TOKEN_EXPIRATION * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key=settings.ACCES_COOKIE_NAME, domain=settings.COOKIE_DOMAIN, path="/")
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME, domain=settings.COOKIE_DOMAIN, path="/api/v1/auth"
    )


@router.post("/login", response_model=TokenResponse, summary="Se connecter")
def login(
    payload: LoginRequest, response: Response, service: UserService = Depends(get_user_service)
) -> TokenResponse:
    tokens = service.login(payload.email, payload.password)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/refresh", response_model=TokenResponse, summary="Rafraîchir l'acces token ")
def refresh_token(
    request: Request, response: Response, service: UserService = Depends(get_user_service)
) -> TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalide ou expiré"
    )
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not token:
        raise credentials_exception
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise credentials_exception
        user_id = int(payload["sub"])
    except (JWTError, ValueError):
        raise credentials_exception from None

    try:
        user = service.get_by_id(user_id)
    except NotFoundError:
        raise credentials_exception from None

    if user.is_suspended or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce compte est suspendu")
    new_access = create_access_token(subject=user.id)
    new_refresh = create_refresh_token(subject=user.id)
    set_auth_cookies(response, new_access, new_refresh)

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Se déconnecter")
def logout(response: Response):
    clear_auth_cookies(response)


@router.get("/me", summary="Retourner profil connecté")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "study_sector": current_user.study_sector,
        "university": current_user.university,
    }
