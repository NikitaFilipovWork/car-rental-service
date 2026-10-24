from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
@permission_classes([])
def api_root(request):
    return Response(
        {
            "users": reverse("users:create", request=request),
            "token": reverse("users:token_obtain_pair", request=request),
            "token_refresh": reverse("users:token_refresh", request=request),
            "me": reverse("users:manage", request=request),
            "cars": reverse("car:car-list", request=request),
            "rentals": reverse("rentals:rental-list", request=request),
            "schema": reverse("schema", request=request),
            "docs": reverse("swagger-ui", request=request),
        }
    )
