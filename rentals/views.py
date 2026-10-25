from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rentals.models import Rental
from rentals.serializers import (
    RentalListViewSerializer,
    RentalDetailViewSerializer,
    RentalCreateViewSerializer,
    EmptySerializer,
)
from rentals.services import rental_service


@extend_schema_view(
    list=extend_schema(
        summary="rentals list",
        description="List rentals with filtering by user and rental status. Customer sees only his own rentals, staff sees all",
    ),
    create=extend_schema(
        summary="rental create",
        description="Create a new rental",
    ),
    retrieve=extend_schema(
        summary="rental detail",
        description="Get a rental by id",
    ),
    return_rental=extend_schema(
        summary="rental return by id",
        description="Return rental car by id. Sets rental's return date = current date. Return available after rental period started",
        responses={status.HTTP_200_OK: RentalDetailViewSerializer},
    ),
    cancel_rental=extend_schema(
        summary="rental cancel by id",
        description="Cancel rental by id. Cancel available before rental period started",
        responses={status.HTTP_200_OK: RentalDetailViewSerializer},
    ),
)
class RentalsViewSet(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet
):
    queryset = Rental.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("user_id", "status")

    @action(detail=True, methods=["post"], url_path="return", url_name="return")
    def return_rental(self, request, *args, **kwargs):
        rental = self.get_object()
        rental = rental_service.return_rental(rental=rental)
        return Response(
            RentalDetailViewSerializer(rental).data, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="cancel",
        url_name="cancel",
    )
    def cancel_rental(self, request, *args, **kwargs):
        rental = self.get_object()
        rental = rental_service.cancel_rental(rental)
        return Response(
            RentalDetailViewSerializer(rental).data, status=status.HTTP_200_OK
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset.select_related("user", "car").order_by("id")

    def perform_create(self, serializer):
        rental = rental_service.create_rental(
            user=self.request.user, **serializer.validated_data
        )
        serializer.instance = rental

    def get_serializer_class(self):
        match self.action:
            case "retrieve":
                return RentalDetailViewSerializer
            case "create":
                return RentalCreateViewSerializer
            case "return_rental":
                return EmptySerializer
            case "cancel_rental":
                return EmptySerializer
            case _:
                return RentalListViewSerializer
