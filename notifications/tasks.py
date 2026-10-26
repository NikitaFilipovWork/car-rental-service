from celery import shared_task
from django.utils import timezone
from requests.exceptions import RequestException

from rentals.models import Rental
from .models import FailedNotification
from .services import send_telegram_message


@shared_task()
def send_telegram_notification(message: str) -> None:
    try:
        send_telegram_message(message)
    except RequestException:
        FailedNotification.objects.create(message=message)


@shared_task()
def retry_failed_notifications() -> None:
    messages = FailedNotification.objects.all()
    for message in messages:
        created_at = timezone.localtime(message.created_at)
        formatted_date = created_at.strftime("%d.%m.%Y %H:%M")
        message_for_send = (
            f"🔄 Delayed notification:\n"
            f"{message.message}\n"
            f"Created at: {formatted_date}"
        )
        try:
            send_telegram_message(message_for_send)
            message.delete()
        except RequestException:
            continue


@shared_task()
def check_overdue_rentals() -> None:
    rentals = Rental.objects.select_related("car", "user").filter(
        end_date__lt=timezone.localdate(),
        actual_return_date__isnull=True,
        status__in=[Rental.RentalStatus.BOOKED, Rental.RentalStatus.OVERDUE],
    )

    for rental in rentals:
        if rental.status == Rental.RentalStatus.BOOKED:
            rental.status = Rental.RentalStatus.OVERDUE
            rental.save(update_fields=["status"])

        days_overdue = (timezone.localdate() - rental.end_date).days

        message = (
            f"⚠️ Status: {rental.status}!!!\n"
            f"Car: {rental.car}\n"
            f"User: {rental.user}\n"
            f"Start date: {rental.start_date}\n"
            f"End date: {rental.end_date}\n"
            f"Days overdue: {days_overdue}"
        )

        try:
            send_telegram_message(message)
        except RequestException:
            FailedNotification.objects.create(message=message)
