"""Public endpoint for availability and price quotes."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.inventory.models import RoomType

from .quote import calculate_quote
from .serializers import QuoteRequestSerializer, QuoteSerializer
from .stay_policy import validate_stay

ERROR_RESPONSE = OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"})


@extend_schema(
    tags=["bookings"],
    request=QuoteRequestSerializer,
    responses={
        status.HTTP_200_OK: QuoteSerializer,
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE,
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def quote(request: Request) -> Response:
    """Return current availability and price without reserving inventory."""

    request_data = QuoteRequestSerializer(data=request.data)
    request_data.is_valid(raise_exception=True)
    data = request_data.validated_data
    stay = validate_stay(data["check_in"], data["check_out"], timezone.now())
    room_type = get_object_or_404(RoomType, slug=data["room_type"])
    result = calculate_quote(
        stay=stay,
        room_type=room_type,
        adults=data["adults"],
        children=data["children"],
    )
    return Response(QuoteSerializer(result).data)
