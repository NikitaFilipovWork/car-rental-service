from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from car.cache import CARS_CACHE_TIMEOUT, get_cars_cache_version
from car.filters import CarFilter
from car.models import Car
from car.permissions import IsAdminOrReadOnly
from car.serializers import CarSerializer


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
