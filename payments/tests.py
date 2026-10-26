from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from payments.helper import create_payment, mark_payment_paid
from payments.models import Payment
from rentals.tests.test_base import (
    StripeMockMixin,
    sample_car,
    sample_rental,
    sample_user,
)

PAID = Payment.PaymentStatus.PAID
PENDING = Payment.PaymentStatus.PENDING
EXPIRED = Payment.PaymentStatus.EXPIRED


def sample_payment(rental, **params):
    defaults = {
        "rental": rental,
        "type": Payment.PaymentType.RENTAL,
        "money_to_pay": Decimal("100.00"),
        "session_id": "cs_test_1",
        "session_url": "https://stripe.test/cs_test_1",
    }
    defaults.update(params)
    return Payment.objects.create(**defaults)


class PaymentTypeTests(TestCase):
    def test_cancellation_fee_value_has_no_trailing_space(self):
        self.assertEqual(Payment.PaymentType.CANCELLATION_FEE, "CANCELLATION_FEE")


class CreatePaymentTests(StripeMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.rental = sample_rental(sample_user(), sample_car())

    @override_settings(SITE_URL="https://rent.example.com/")
    def test_without_request_uses_site_url(self):
        payment = create_payment(self.rental, Payment.PaymentType.RENTAL)

        kwargs = self.stripe_session_create.call_args.kwargs
        self.assertTrue(
            kwargs["success_url"].startswith(
                "https://rent.example.com/api/payments/success/"
            )
        )
        self.assertEqual(
            kwargs["cancel_url"], "https://rent.example.com/api/payments/cancel/"
        )
        self.assertEqual(payment.status, PENDING)


@patch("payments.helper.notify_payment_successful")
class MarkPaymentPaidTests(TestCase):
    def setUp(self):
        self.payment = sample_payment(sample_rental(sample_user(), sample_car()))

    def test_marks_paid_and_notifies_once(self, mock_notify):
        mark_payment_paid(self.payment.session_id)
        mark_payment_paid(self.payment.session_id)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, PAID)
        mock_notify.assert_called_once()

    def test_unknown_session_is_ignored(self, mock_notify):
        self.assertIsNone(mark_payment_paid("cs_unknown"))
        mock_notify.assert_not_called()


@patch("payments.helper.notify_payment_successful")
class StripeWebhookTests(APITestCase):
    url = reverse("payments:payment-webhook")

    def setUp(self):
        self.payment = sample_payment(sample_rental(sample_user(), sample_car()))

    def _event(self, event_type, **session):
        session.setdefault("id", self.payment.session_id)
        return {"type": event_type, "data": {"object": session}}

    @patch("payments.views.stripe.Webhook.construct_event")
    def test_completed_session_marks_payment_paid(self, mock_event, mock_notify):
        mock_event.return_value = self._event(
            "checkout.session.completed", payment_status="paid"
        )

        res = self.client.post(self.url, data="{}", content_type="application/json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, PAID)
        mock_notify.assert_called_once()

    @patch("payments.views.stripe.Webhook.construct_event")
    def test_expired_session_marks_payment_expired(self, mock_event, mock_notify):
        mock_event.return_value = self._event("checkout.session.expired")

        self.client.post(self.url, data="{}", content_type="application/json")

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, EXPIRED)
        mock_notify.assert_not_called()

    def test_invalid_signature_rejected(self, mock_notify):
        res = self.client.post(
            self.url,
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="bad",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, PENDING)
