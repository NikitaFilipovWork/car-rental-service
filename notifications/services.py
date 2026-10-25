import requests

from django.conf import settings


def send_telegram_message(message: str) -> None:
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    response = requests.post(send_url, data=payload, timeout=10)

    response.raise_for_status()
