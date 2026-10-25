from kombu.exceptions import OperationalError

from notifications.models import FailedNotification
from notifications.tasks import send_telegram_notification


def _dispatch_notification(message: str) -> None:
    try:
        send_telegram_notification.delay(message)
    except OperationalError:
        FailedNotification.objects.create(message=message)


def notify_rental_created(rental) -> None:
    message = (
        f"🚗 New rental #{rental.id}\n"
        f"Customer: {rental.user}\n"
        f"Car: {rental.car}\n"
        f"Start date: {rental.start_date}\n"
        f"End date: {rental.end_date}\n"
        f"Price per day: {rental.price_per_day}\n"
        f"Status: {rental.status}"
    )

    _dispatch_notification(message)


def notify_rental_returned(rental) -> None:
    message = (
        f"🔑 Rental returned #{rental.id}\n"
        f"Customer: {rental.user}\n"
        f"Car: {rental.car}\n"
        f"Start date: {rental.start_date}\n"
        f"End date: {rental.end_date}\n"
        f"Actual return date: {rental.actual_return_date}\n"
        f"Status: {rental.status}"
    )

    _dispatch_notification(message)


def notify_rental_canceled(rental) -> None:
    message = (
        f"❌ Rental canceled #{rental.id}\n"
        f"Customer: {rental.user}\n"
        f"Car: {rental.car}\n"
        f"Start date: {rental.start_date}\n"
        f"End date: {rental.end_date}\n"
        f"Status: {rental.status}"
    )

    _dispatch_notification(message)


def notify_payment_successful(payment_id, rental_id, amount) -> None:
    message = (
        f"💳 Payment successful!\n"
        f"Payment ID: {payment_id}\n"
        f"Rental ID: {rental_id}\n"
        f"Amount: {amount}\n"
        f"Status: PAID"
    )

    _dispatch_notification(message)
