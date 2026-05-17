from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review import ReviewService

router = APIRouter(tags=["reviews"])


@router.post(
    "/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Laisser un avis sur une prestation terminée",
)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewResponse:
    service = ReviewService(db)
    review = service.create_review(buyer_id=current_user.id, payload=payload)
    return ReviewResponse.model_validate(review)


@router.get(
    "/services/{service_id}/reviews",
    response_model=list[ReviewResponse],
    summary="Lister les avis d'un service",
)
def list_service_reviews(
    service_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[ReviewResponse]:
    service = ReviewService(db)
    reviews, _total = service.list_service_reviews(service_id=service_id, skip=skip, limit=limit)
    return [ReviewResponse.model_validate(r) for r in reviews]
