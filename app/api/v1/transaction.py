from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.transaction import TransactionRead
from app.services.transaction import PaymentService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/me", response_model=list[TransactionRead], summary="Lister mes transactions")
def list_my_transactions(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TransactionRead]:
    service = PaymentService(db)
    transactions, _total = service.list_user_transaction(
        user_id=current_user.id, skip=skip, limit=limit
    )
    return [TransactionRead.model_validate(transaction) for transaction in transactions]


@router.get("/{transaction_id}", response_model=TransactionRead, summary="Détail d'une transaction")
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    service = PaymentService(db)
    transaction = service.get_transaction(transaction_id=transaction_id, user_id=current_user.id)
    return TransactionRead.model_validate(transaction)
