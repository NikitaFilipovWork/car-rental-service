from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from car.filters import CarFilter
from car.models import Car
from car.permissions import IsAdminOrReadOnly
from car.serializers import CarSerializer


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CarFilter
