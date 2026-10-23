from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import api_root

urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/users/", include("users.urls", namespace="users")),
    path("api/cars/", include("car.urls", namespace="car")),
    path("api/rentals/", include("rentals.urls", namespace="rentals")),
    # path("api/payments/", include("payments.urls", namespace="payments")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
