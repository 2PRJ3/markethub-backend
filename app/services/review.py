from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ForbiddenActionError,
    IdempotencyConflictError,
    InvalidStateTransitionError,
    NotFoundError,
)
from app.models.review import Review
from app.repositories.order_item import OrderItemRepository
from app.repositories.review import ReviewRepository
from app.repositories.service import ServiceRepository
from app.schemas.review import ReviewCreate
from app.utils.enums import OrderItemStatus


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.order_item_repo = OrderItemRepository(db)
        self.service_repo = ServiceRepository(db)

    def create_review(self, buyer_id: int, payload: ReviewCreate) -> Review:
        item = self.order_item_repo.get_with_relations(payload.order_item_id)
        if item is None:
            raise NotFoundError("Ligne de commande introuvable.")

        if item.order.buyer_id != buyer_id:
            raise ForbiddenActionError(
                "Vous ne pouvez pas laisser un avis sur cette ligne de commande."
            )

        if item.status != OrderItemStatus.COMPLETED:
            raise InvalidStateTransitionError(
                "Vous ne pouvez laisser un avis que sur une prestation terminée."
            )

        review = Review(
            order_item_id=payload.order_item_id,
            buyer_id=buyer_id,
            service_id=item.service_id,
            rating=payload.rating,
            comment=payload.comment,
        )

        try:
            self.review_repo.create(review)
            self._refresh_service_stats(item.service_id)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise IdempotencyConflictError("Un avis existe déjà pour cette prestation.") from None

        self.db.refresh(review)
        return review

    def list_service_reviews(
        self, service_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Review], int]:
        service = self.service_repo.get_by_id(service_id)
        if service is None:
            raise NotFoundError("Service introuvable.")

        reviews = self.review_repo.list_by_service(service_id, skip=skip, limit=limit)
        total = self.review_repo.count_by_service(service_id)
        return reviews, total

    def admin_delete_review(self, review_id: int) -> None:
        review = self.review_repo.get_by_id(review_id)
        if review is None:
            raise NotFoundError("Avis introuvable.")

        service_id = review.service_id
        self.review_repo.delete(review)
        self._refresh_service_stats(service_id)
        self.db.commit()

    def _refresh_service_stats(self, service_id: int) -> None:
        avg, count = self.review_repo.get_stats_by_service(service_id)
        service = self.service_repo.get_by_id(service_id)
        if service is not None:
            self.service_repo.update(service, {"average_rating": avg, "reviews_count": count})
