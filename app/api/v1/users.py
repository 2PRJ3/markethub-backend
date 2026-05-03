from fastapi import Depends, HTTPException, APIRouter, status


from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPublic, PasswordChange
from app.models.user import User


from app.services.user_service import UserService
from app.api.deps import get_user_service, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Inscription d'un nouvel utilisateur")
def register_user( payload: UserCreate, service: UserService = Depends(get_user_service)) -> UserResponse:
    user = service.create_user(payload)
    return user

@router.get("/{user_id}", response_model=UserPublic, summary="Profil d'un utilisateur")
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserPublic:
    return service.get_by_id((user_id))

@router.patch("/me", response_model=UserResponse, summary="Mettre à jour le profil utilisateur")
def update_user(payload: UserUpdate, current_user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)) -> UserResponse:
    return service.update_profile(current_user.id, payload)

@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT, summary="Changer le mot de passe")
def change_password(user_id: int, payload: PasswordChange, service: UserService = Depends(get_user_service)) -> None:
    service.change_password(user_id, payload)