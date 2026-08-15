"""Public HTTP endpoints for booking quotes and customer-owned bookings."""

from uuid import UUID

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.inventory.models import RoomType

from .quote import calculate_quote
from .selectors import active_bookings, get_owned_booking, history_bookings
from .serializers import (
    BookingListSerializer,
    BookingSerializer,
    QuoteRequestSerializer,
    QuoteSerializer,
)
from .services import cancel_booking, expire_stale_holds
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


@extend_schema(
    tags=["bookings"],
    responses={
        status.HTTP_200_OK: BookingListSerializer,
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSE,
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_list(request: Request) -> Response:
    """Return the current customer's active and historical bookings."""

    now = timezone.now()
    expire_stale_holds(now)
    customer_id = request.user.pk
    today = timezone.localdate()
    return Response(
        BookingListSerializer(
            {
                "active": active_bookings(customer_id, today),
                "history": history_bookings(customer_id, today),
            }
        ).data
    )


@extend_schema(
    tags=["bookings"],
    responses={
        status.HTTP_200_OK: BookingSerializer,
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSE,
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSE,
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_detail(request: Request, reference: UUID) -> Response:
    """Return one booking only when it belongs to the authenticated customer."""

    expire_stale_holds(timezone.now())
    booking = get_owned_booking(request.user.pk, reference)
    return Response(BookingSerializer(booking).data)


@extend_schema(
    tags=["bookings"],
    responses={
        status.HTTP_200_OK: BookingSerializer,
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSE,
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSE,
        status.HTTP_409_CONFLICT: ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def booking_cancel(request: Request, reference: UUID) -> Response:
    """Cancel one owned booking through the booking lifecycle service."""

    now = timezone.now()
    expire_stale_holds(now)
    booking = get_owned_booking(request.user.pk, reference)
    return Response(BookingSerializer(cancel_booking(booking, now)).data)
