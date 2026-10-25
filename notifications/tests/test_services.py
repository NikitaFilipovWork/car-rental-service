from unittest.mock import patch

import requests
from django.test import SimpleTestCase, override_settings

from notifications.services import send_telegram_message


@override_settings(
    TELEGRAM_BOT_TOKEN="test_token",
    TELEGRAM_CHAT_ID="-123456789",
)
class TelegramServiceTests(SimpleTestCase):
    @patch("notifications.services.requests.post")
    def test_send_telegram_message_success(self, mock_post):
        send_telegram_message("Test message")

        mock_post.assert_called_once_with(
            "https://api.telegram.org/bottest_token/sendMessage",
            data={
                "chat_id": "-123456789",
                "text": "Test message",
            },
            timeout=10,
        )

        mock_post.return_value.raise_for_status.assert_called_once_with()

    @patch("notifications.services.requests.post")
    def test_send_telegram_message_http_error(self, mock_post):
        mock_post.return_value.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("400 Bad Request")
        )

        with self.assertRaises(requests.exceptions.HTTPError):
            send_telegram_message("Test message")

    @patch("notifications.services.requests.post")
    def test_send_telegram_message_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        with self.assertRaises(requests.exceptions.ConnectionError):
            send_telegram_message("Test message")
