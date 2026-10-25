from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse

from payments.models import Payment
from rentals.models import Rental

stripe.api_key = settings.STRIPE_SECRET_KEY

PaymentType = Payment.PaymentType


def calculate_rental_price(rental: Rental) -> Decimal:
    days = (rental.end_date - rental.start_date).days + 1
    return rental.price_per_day * days


def calculate_cancellation_fee(rental: Rental) -> Decimal:
    return calculate_rental_price(rental) * Decimal("0.5")


def calculate_overdue_fee(rental: Rental) -> Decimal:
    overdue_days = (rental.actual_return_date - rental.end_date).days
    if overdue_days <= 0:
        return Decimal("0")
    return rental.price_per_day * overdue_days * settings.FINE_MULTIPLIER


AMOUNT_CALCULATORS = {
    PaymentType.RENTAL: calculate_rental_price,
    PaymentType.CANCELLATION_FEE: calculate_cancellation_fee,
    PaymentType.OVERDUE_FEE: calculate_overdue_fee,
}


def create_payment(rental: Rental, payment_type: str, request) -> Payment:
    amount = AMOUNT_CALCULATORS[payment_type](rental).quantize(Decimal("0.01"))

    success_url = (
        request.build_absolute_uri(reverse("payments:payment-success"))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri(reverse("payments:payment-cancel"))

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(amount * 100),
                    "product_data": {
                        "name": f"{payment_type} for rental #{rental.id}",
                    },
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return Payment.objects.create(
        rental=rental,
        type=payment_type,
        money_to_pay=amount,
        session_id=session.id,
        session_url=session.url,
    )

def is_session_paid(session_id: str) -> bool:
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status == "paid"