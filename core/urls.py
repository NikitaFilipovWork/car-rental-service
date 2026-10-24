from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import cache_page
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import api_root

SCHEMA_CACHE_TIMEOUT = 0 if settings.DEBUG else 60 * 60 * 24  # 1 день

urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/users/", include("users.urls", namespace="users")),
    path("api/cars/", include("car.urls", namespace="car")),
    path("api/rentals/", include("rentals.urls", namespace="rentals")),
    path(
        "api/schema/",
        cache_page(SCHEMA_CACHE_TIMEOUT)(SpectacularAPIView.as_view()),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
