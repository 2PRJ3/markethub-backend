from app.utils.card_number_algo import algo_luhn
from app.utils.enums import PaymentFailureReason

_MAGIC_CARDS: dict[str, PaymentFailureReason | None] = {
    "4242424242424242": None,
    "4000000000000002": PaymentFailureReason.CARD_DECLINED,
    "4000000000009995": PaymentFailureReason.INSUFFICIENT_FUNDS,
    "4000000000000069": PaymentFailureReason.PROCESSING_ERROR,
}


def simulate_payment(card_number: str) -> PaymentFailureReason | None:
    if card_number in _MAGIC_CARDS:
        return _MAGIC_CARDS[card_number]
    if not algo_luhn(card_number):
        return PaymentFailureReason.INVALID_CARD
    return None
