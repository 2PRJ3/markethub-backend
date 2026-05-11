from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.user import PasswordChange, UserCreate, UserPublic, UserResponse, UserUpdate
from app.services.user_service import UserService
router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouvel utilisateur",
)
def register_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserResponse:
    user = service.create_user(payload)
    return user


@router.get("/{user_id}", response_model=UserPublic, summary="Profil d'un utilisateur")
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserPublic:
    return service.get_by_id(user_id)


@router.patch("/me", response_model=UserResponse, summary="Mettre à jour le profil utilisateur")
def update_user(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return service.update_profile(current_user.id, payload)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Changer le mot de passe",
)
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    service.change_password(current_user.id, payload)
