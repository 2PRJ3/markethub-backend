from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Repository générique pour CRUD
    """
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Récupérer un objet par son id
        """
        return self.db.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Récupérer tous les objets avec pagination
        """
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, obj_in: dict) -> ModelType:
        """
        Crée un nouvel objet
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict) -> None:
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