from typing import TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType]:
    """
    Repository générique pour CRUD
    """

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> ModelType | None:
        """
        Récupérer un objet par son id
        """
        return self.db.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Récupérer tous les objets avec pagination
        """
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, db_obj: ModelType) -> ModelType:
        """
        Crée un nouvel objet
        """
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """
        Mettre à jour un objet existant
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> None:
        """
        Supprimer un objet
        """
        self.db.delete(db_obj)
        self.db.flush()

    def count(self) -> int:
        """
        Compter le nombre d'objets
        """
        stmt = select(func.count()).select_from(self.model)
        return self.db.execute(stmt).scalar_one()
