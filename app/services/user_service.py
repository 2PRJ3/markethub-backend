from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, PasswordChange
from app.utils.enums import UserRole

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import NotFoundError, EmailAlreadyExistsError, InvalidCredentialsError, UserSuspendedError
from app.schemas.auth import TokenResponse


class UserService:
    def __init__(self, db:Session):
        self.db = db
        self.repo = UserRepository(db)

    def create_user(self, data: UserCreate) -> User:
        normalized_email = data.email.lower().strip()

        if self.repo.email_exists(normalized_email):
            raise EmailAlreadyExistsError(
                f"L'email {normalized_email} est déjà utilisé"
            )

        user = User(
            email=normalized_email,
            password_hash=hash_password(data.password),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            university=data.university.strip() if data.university else None,
            study_sector=data.study_sector.strip() if data.study_sector else None,
            bio=data.bio,
            avatar_url=data.avatar_url,
            role=UserRole.USER,
            is_active=True,
            is_suspended=False
        )

        self.repo.create(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(f"Utilisateur {user_id} introuvable.")
        return user

    def get_by_email(self, email: str) -> User:
        user = self.repo.get_by_email(email.lower().strip())

        if not user:
            raise NotFoundError(f"Utilisateur avec email :  {email} introuvable.")
        return user

    def update_profile(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_by_id(user_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if isinstance(value, str):
                update_data[field] = value.strip() or None
        self.repo.update(user, update_data)
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user_id: int, data: PasswordChange) -> None:
        user = self.get_by_id(user_id)

        if not verify_password(data.current_password, user.password_hash):
            raise InvalidCredentialsError("Mot de passe actuel incorrecte")

        user.password_hash = hash_password(data.new_password.strip())
        self.db.commit()

    def authenticate(self, email: str, password: str) -> User:
        try:
            user = self.get_by_email(email)
        except NotFoundError:
            raise InvalidCredentialsError("Email ou mot de passe invalide")
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Email ou mot de passe invalide")

        if user.is_suspended or not user.is_active:
            raise UserSuspendedError("Ce compte est suspendu")

        return user

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.authenticate(email, password)
        return TokenResponse(
            access_token=create_access_token(subject=user.id),
            refresh_token=create_refresh_token(subject=user.id),
        )

    def suspend_user(self, user_id: int) -> User:
        user = self.get_by_id(user_id)
        user = self.repo.suspend(user)

        self.db.commit()
        self.db.refresh(user)
        return user

    def reactivate_user(self, user_id: int) -> User:
        user = self.get_by_id(user_id)
        user = self.repo.reactivate(user)
        self.db.commit()
        self.db.refresh(user)
        return user