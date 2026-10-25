from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase

from notifications.rental_notifications import notify_payment_successful


class PaymentNotificationTests(SimpleTestCase):
    @patch("notifications.rental_notifications._dispatch_notification")
    def test_notify_payment_successful(self, mock_dispatch):
        notify_payment_successful(
            payment_id=15,
            rental_id=8,
            amount=Decimal("125.00"),
        )

        expected_message = (
            "💳 Payment successful!\n"
            "Payment ID: 15\n"
            "Rental ID: 8\n"
            "Amount: 125.00\n"
            "Status: PAID"
        )

        mock_dispatch.assert_called_once_with(expected_message)
