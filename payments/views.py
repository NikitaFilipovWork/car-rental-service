import stripe
from django.conf import settings
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from payments.helper import handle_stripe_event, is_session_paid, mark_payment_paid
from payments.models import Payment
from payments.serializers import PaymentDetailSerializer, PaymentListSerializer


@extend_schema_view(
    list=extend_schema(
        summary="payments list",
        description="Customer sees only payments of his own rentals, staff sees all",
    ),
    retrieve=extend_schema(
        summary="payment detail",
        description="Payment with short rental info",
    ),
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    filterset_fields = ("status", "type")

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("rental", "rental__car", "rental__user")
        )
        if not self.request.user.is_staff:
            queryset = queryset.filter(rental__user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentListSerializer

    @extend_schema(
        summary="confirm Stripe payment",
        description=(
            "Stripe redirects here after a successful checkout. "
            "Checks the session in Stripe and marks the payment as PAID."
        ),
        parameters=[
            OpenApiParameter(
                "session_id",
                str,
                required=True,
                description="Stripe Checkout Session id",
            )
        ],
        responses={status.HTTP_200_OK: PaymentDetailSerializer},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="success",
        url_name="success",
        permission_classes=(AllowAny,),
    )
    def success(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"detail": "session_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(Payment, session_id=session_id)

        if not is_session_paid(session_id):
            return Response(
                {"detail": "Payment is not completed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = mark_payment_paid(payment.session_id)

        return Response(PaymentDetailSerializer(payment).data)

    @extend_schema(
        summary="Stripe payment paused",
        description="Stripe redirects here when the user leaves the checkout page.",
        responses={status.HTTP_200_OK: None},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="cancel",
        url_name="cancel",
        permission_classes=(AllowAny,),
    )
    def cancel(self, request):
        return Response(
            {
                "detail": (
                    "Payment was paused. You can pay later using the same link, "
                    "but the session is available only for 24 hours."
                )
            }
        )

    @extend_schema(
        summary="Stripe webhook",
        description=(
            "Stripe calls this endpoint about Checkout Session events. "
            "Marks payments as PAID or EXPIRED even if the user never "
            "returned to the success page."
        ),
        request=None,
        responses={status.HTTP_200_OK: None},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="webhook",
        url_name="webhook",
        permission_classes=(AllowAny,),
        authentication_classes=(),
        throttle_classes=(),
    )
    def webhook(self, request):
        signature = request.headers.get("Stripe-Signature", "")
        try:
            event = stripe.Webhook.construct_event(
                request.body, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.SignatureVerificationError):
            return Response(
                {"detail": "Invalid Stripe webhook"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        handle_stripe_event(event)
        return Response(status=status.HTTP_200_OK)
