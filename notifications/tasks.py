from celery import shared_task

from .services import send_telegram_message


@shared_task()
def send_telegram_notification(message: str) -> None:
    send_telegram_message(message)
