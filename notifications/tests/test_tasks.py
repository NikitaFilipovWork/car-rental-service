from unittest.mock import patch

from django.test import SimpleTestCase

from notifications.tasks import send_telegram_notification


class TelegramTaskTests(SimpleTestCase):
    @patch("notifications.tasks.send_telegram_message")
    def test_send_telegram_notification(self, mock_send):
        send_telegram_notification("Test notification")

        mock_send.assert_called_once_with("Test notification")
