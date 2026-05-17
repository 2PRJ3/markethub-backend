from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def list_by_service(self, service_id: int, skip: int = 0, limit: int = 20) -> list[Review]:
        stmt = (
            select(Review)
            .where(Review.service_id == service_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_by_service(self, service_id: int) -> int:
        stmt = select(func.count(Review.id)).where(Review.service_id == service_id)
        return self.db.execute(stmt).scalar_one()

    def get_stats_by_service(self, service_id: int) -> tuple[float | None, int]:
        stmt = select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("count"),
        ).where(Review.service_id == service_id)
        result = self.db.execute(stmt).one()
        avg = float(result.avg_rating) if result.avg_rating is not None else None
        return avg, result.count
