from rest_framework import routers

from rentals.views import RentalsViewSet

app_name = "rentals"


router = routers.DefaultRouter()
router.register("", RentalsViewSet)
urlpatterns = router.urls
