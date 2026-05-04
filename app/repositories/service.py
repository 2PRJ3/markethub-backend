
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(Service, db)

    def get_by_seller(self, seller_id: int, skip: int = 0, limit: int = 100) -> list[Service]:
        stmt = select(self.model).where(self.model.seller_id == seller_id).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_category(self, category_id: int, skip: int = 0, limit: int = 100) -> list[Service]:
        stmt = (
            select(self.model)
            .where(self.model.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_by_seller(self, seller_id: int) -> int:
        stmt = select(func.count()).select_from(self.model).where(self.model.seller_id == seller_id)
        return self.db.execute(stmt).scalar_one()
