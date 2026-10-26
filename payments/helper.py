from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import APIException

from notifications.rental_notifications import notify_payment_successful
from payments.models import Payment
from rentals.models import Rental

stripe.api_key = settings.STRIPE_SECRET_KEY

PaymentType = Payment.PaymentType
PaymentStatus = Payment.PaymentStatus


class PaymentServiceError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Payment service is unavailable. Please try again later."
    default_code = "payment_service_unavailable"


def _stripe_error(error: stripe.StripeError) -> PaymentServiceError:
    # Stripe's user_message is safe to show (e.g. "amount too small"), others are not
    return PaymentServiceError(getattr(error, "user_message", None) or None)


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


def _absolute_url(path: str, request=None) -> str:
    if request is not None:
        return request.build_absolute_uri(path)
    return settings.SITE_URL.rstrip("/") + path


def _redirect_urls(request=None) -> tuple[str, str]:
    """Where Stripe sends the user after checkout: the web app or the API."""
    if settings.FRONTEND_URL:
        frontend = settings.FRONTEND_URL.rstrip("/")
        # Query goes before the hash so the web app's hash router keeps working
        return (
            f"{frontend}/?session_id={{CHECKOUT_SESSION_ID}}#/payments/success",
            f"{frontend}/#/payments?canceled=true",
        )

    success_url = (
        _absolute_url(reverse("payments:payment-success"), request)
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    return success_url, _absolute_url(reverse("payments:payment-cancel"), request)


def create_payment(rental: Rental, payment_type: str, request=None) -> Payment:
    amount = AMOUNT_CALCULATORS[payment_type](rental).quantize(Decimal("0.01"))

    try:
        session = _create_checkout_session(rental, payment_type, amount, request)
    except stripe.StripeError as error:
        raise _stripe_error(error) from error

    return Payment.objects.create(
        rental=rental,
        type=payment_type,
        money_to_pay=amount,
        session_id=session.id,
        session_url=session.url,
    )


def _create_checkout_session(rental, payment_type, amount, request):
    success_url, cancel_url = _redirect_urls(request)
    return stripe.checkout.Session.create(
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
        metadata={"rental_id": rental.id, "payment_type": payment_type},
        success_url=success_url,
        cancel_url=cancel_url,
    )


def is_session_paid(session_id: str) -> bool:
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError as error:
        raise _stripe_error(error) from error
    return session.payment_status == "paid"


def mark_payment_paid(session_id: str) -> Payment | None:
    """Mark payment as PAID once, even if success redirect and webhook race."""
    with transaction.atomic():
        payment = (
            Payment.objects.select_for_update().filter(session_id=session_id).first()
        )
        if payment is None or payment.status == PaymentStatus.PAID:
            return payment
        payment.status = PaymentStatus.PAID
        payment.save(update_fields=["status"])

    notify_payment_successful(payment.id, payment.rental_id, payment.money_to_pay)
    return payment


def mark_payment_expired(session_id: str) -> None:
    Payment.objects.filter(session_id=session_id, status=PaymentStatus.PENDING).update(
        status=PaymentStatus.EXPIRED
    )


def handle_stripe_event(event) -> None:
    session = event["data"]["object"]
    if event["type"] in (
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    ):
        if session.get("payment_status") == "paid":
            mark_payment_paid(session["id"])
    elif event["type"] == "checkout.session.expired":
        mark_payment_expired(session["id"])
