from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from car.cache import CARS_CACHE_TIMEOUT, get_cars_cache_version
from car.filters import CarFilter
from car.models import Car
from car.permissions import IsAdminOrReadOnly
from car.serializers import CarImageSerializer, CarSerializer


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all().order_by("id")
    serializer_class = CarSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = CarFilter
    ordering_fields = ("daily_rate", "year", "brand", "model")
    search_fields = ("brand", "model")

    def _cached_response(self, request, action, *args, **kwargs):
        version = get_cars_cache_version()
        key = f"cars:v{version}:{action}:{request.get_full_path()}"

        data = cache.get(key)
        if data is None:
            data = getattr(super(), action)(request, *args, **kwargs).data
            cache.set(key, data, CARS_CACHE_TIMEOUT)

        return Response(data)

    def list(self, request, *args, **kwargs):
        return self._cached_response(request, "list", *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return self._cached_response(request, "retrieve", *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return CarImageSerializer
        return CarSerializer

    @extend_schema(
        summary="upload car image",
        description="Staff only. Replaces the current image of the car.",
        request={"multipart/form-data": CarImageSerializer},
        responses={status.HTTP_200_OK: CarImageSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="upload-image",
        url_name="upload-image",
        parser_classes=(MultiPartParser, FormParser),
    )
    def upload_image(self, request, pk=None):
        car = self.get_object()
        serializer = self.get_serializer(car, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
