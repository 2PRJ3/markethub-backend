from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Récupérer l'utilisateur par email
        """
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def email_exists(self, email: str) -> bool:
        """ Vérifier si l'email existe"""
        stmt = select(func.count()).select_from(User).where(User.email == email.lower())
        result = self.db.execute(stmt).scalar_one()
        return result > 0

    # def list_users(self, skip: int = 0, limit: int = 20, search: Optional[str] = None, is_suspended: Optional[bool] = None) -> List[User]:
    #     """
    #     Liste paginée des utilisateurs pour l'admin
    #     Recherche textuelle (email, prénom, nom)
    #     """
    #     stmt = select(User)
    #
    #     if search:
    #         pattern = f"%{search}%"
    #         stmt = stmt.where(
    #             or_(
    #                 func.lower(User.email).like(pattern),
    #                 func.lower(User.first_name).like(pattern),
    #                 func.lower(User.last_name).like(pattern),
    #             )
    #         )
    #     if is_suspended is not None:
    #         stmt = stmt.where(User.is_suspended.is_(is_suspended))
    #
    #     stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
    #
    #     return list(self.db.execute(stmt).scalars().all())

    def suspend(self, user:User) -> User:
        """ Suspendre un utilisateur"""
        user.is_suspended = True
        user.is_active = False
        self.db.flush()
        self.db.refresh(user)
        return user

    def reactivate(self, user:User) -> User:
        """ Réactiver un utilisateur"""
        user.is_suspended = False
        user.is_active = True
        self.db.flush()
        self.db.refresh(user)
        return user