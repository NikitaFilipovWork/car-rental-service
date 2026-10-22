from django_filters.rest_framework import DjangoFilterBackend
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


class RentalsViewSet(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet
):
    queryset = Rental.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("user_id", "status")

    @action(
        detail=True,
        methods=["post"],
        url_path="return",
    )
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
