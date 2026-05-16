from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderItemStatusUpdate,
    OrderResponse,
    OrderSummary,
    SellerOrderItemResponse,
)
from app.schemas.transaction import (
    OrderPaymentSummary,
    PaymentRequest,
    PaymentResponse,
    TransactionRead,
)
from app.services.order import OrderService
from app.services.transaction import PaymentService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une commande",
)
def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderResponse:
    service = OrderService(db)
    order = service.create_order(buyer_id=current_user.id, payload=payload)
    return OrderResponse.model_validate(order)


@router.get(
    "/me", response_model=list[OrderSummary], summary="Lister les commandes en tant qu'acheteur"
)
def list_my_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderSummary]:
    service = OrderService(db)
    orders, _total = service.list_buyer_orders(buyer_id=current_user.id, skip=skip, limit=limit)
    return [
        OrderSummary(
            id=order.id,
            total_amount=order.total_amount,
            status=order.status,
            items_count=len(order.items),
            created_at=order.created_at,
        )
        for order in orders
    ]


@router.get(
    "/me/sales",
    response_model=list[SellerOrderItemResponse],
    summary="Lister les ventes du vendeur",
)
def list_my_sales(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SellerOrderItemResponse]:
    service = OrderService(db)
    items, _total = service.list_seller_sales(seller_id=current_user.id, skip=skip, limit=limit)
    return [SellerOrderItemResponse.model_validate(item) for item in items]


@router.get("/{order_id}", response_model=OrderResponse, summary="Détail d'une commande")
def get_order(
    order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> OrderResponse:
    service = OrderService(db)
    order = service.get_order(order_id, user_id=current_user.id)
    return OrderResponse.model_validate(order)


@router.patch(
    "/{order_id}/items/{item_id}/status",
    response_model=OrderResponse,
    summary="Changer les statut d'une commande",
)
def update_item_status(
    order_id: int,
    item_id: int,
    payload: OrderItemStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderResponse:
    service = OrderService(db)
    service.update_item_status(item_id=item_id, user_id=current_user.id, new_status=payload.status)
    order = service.get_order(order_id=order_id, user_id=current_user.id)
    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/pay",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Pour payer une commande",
)
def pay_order(
    order_id: int,
    payload: PaymentRequest,
    idempotency_key: UUID | None = Header(default=None, alias="idempotency_key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    service = PaymentService(db)
    transaction, order = service.pay_order(
        order_id=order_id, idempotency_key=idempotency_key, payment=payload, user_id=current_user.id
    )
    return PaymentResponse(
        transaction=TransactionRead.model_validate(transaction),
        order=OrderPaymentSummary(id=order.id, status=order.status),
    )


@router.post("/{order_id}/cancel", response_model=OrderResponse, summary="Annuler une commande")
def cancel_order(
    order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> OrderResponse:
    service = OrderService(db)
    order = service.cancel_order(order_id=order_id, user_id=current_user.id)
    return OrderResponse.model_validate(order)
