from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models.user import User
from app.schemas.review import AdminReviewResponse
from app.services.review import ReviewService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/services/{service_id}/reviews",
    response_model=list[AdminReviewResponse],
    summary="Lister les avis d'un service (modération)",
)
def admin_list_service_reviews(
    service_id: int,
    skip: int = 0,
    limit: int = 50,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminReviewResponse]:
    service = ReviewService(db)
    reviews, _total = service.list_service_reviews(service_id=service_id, skip=skip, limit=limit)
    return [AdminReviewResponse.model_validate(r) for r in reviews]


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un avis (modération)",
)
def admin_delete_review(
    review_id: int,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    service = ReviewService(db)
    service.admin_delete_review(review_id=review_id)
