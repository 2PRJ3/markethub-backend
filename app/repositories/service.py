from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.repositories.base import BaseRepository
from app.schemas.service import ServiceSearchParams
from app.utils.enums import ServiceStatus


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

    def get_many_by_ids(self, ids: list[int]) -> list[Service]:
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(ids))
        return list(self.db.execute(stmt).scalars().all())

    def search(self, params: ServiceSearchParams, skip: int = 0, limit: int = 100) -> list[Service]:
        stmt = self._build_search_stmt(params)
        stmt = self._apply_search_ordering(stmt, params)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_search(self, params: ServiceSearchParams) -> int:
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply_search_filters(stmt, params)
        return self.db.execute(stmt).scalar_one()

    def _build_search_stmt(self, params: ServiceSearchParams):
        stmt = select(self.model)
        return self._apply_search_filters(stmt, params)

    def _apply_search_filters(self, stmt, params: ServiceSearchParams):
        stmt = stmt.where(self.model.status == ServiceStatus.ACTIVE)

        if params.category_id is not None:
            stmt = stmt.where(self.model.category_id == params.category_id)

        if params.q:
            tsquery = func.plainto_tsquery("french", params.q)
            stmt = stmt.where(self.model.search_vector.op("@@")(tsquery))

        return stmt

    def _apply_search_ordering(self, stmt, params: ServiceSearchParams):

        if params.q:
            tsquery = func.plainto_tsquery("french", params.q)
            rank = func.ts_rank(self.model.search_vector, tsquery)
            return stmt.order_by(rank.desc(), self.model.created_at.desc())

        return stmt.order_by(self.model.created_at.desc())
