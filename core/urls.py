from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/cars/", include("car.urls", namespace="car")),
    path("api-auth/", include("rest_framework.urls")),
]