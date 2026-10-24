from unittest.mock import patch

from django.test import TestCase
from requests.exceptions import RequestException

from notifications.models import FailedNotification
from notifications.tasks import send_telegram_notification


class FailedNotificationTests(TestCase):
    @patch("notifications.tasks.send_telegram_message")
    def test_failed_notification_is_saved(self, mock_send):
        mock_send.side_effect = RequestException("Telegram unavailable")

        send_telegram_notification("Test notification")

        self.assertTrue(
            FailedNotification.objects.filter(
                message="Test notification"
            ).exists()
        )
