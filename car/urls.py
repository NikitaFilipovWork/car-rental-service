from rest_framework import routers

from car.views import CarViewSet

app_name = "car"

router = routers.DefaultRouter()
router.register("", CarViewSet)

urlpatterns = router.urls
