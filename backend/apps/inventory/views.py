"""Thin read-only public HTTP entry points for the inventory catalog."""

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .models import RoomType
from .serializers import RoomTypeFilterSerializer, RoomTypeSerializer

ERROR_RESPONSE = OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"})
ROOM_TYPE_FILTER_PARAMETERS = [
    OpenApiParameter(
        name="adults",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Минимальная вместимость по взрослым; целое число от 1.",
    ),
    OpenApiParameter(
        name="children",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Минимальная вместимость по детям; целое число от 0.",
    ),
    OpenApiParameter(
        name="amenity",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        many=True,
        description="Повторяемый slug удобства; категория должна содержать все значения.",
    ),
]


def room_type_queryset() -> QuerySet[RoomType]:
    return RoomType.objects.prefetch_related("amenities", "images")


def room_type_filter_data(request: Request) -> dict[str, object]:
    data: dict[str, object] = {"amenity": request.query_params.getlist("amenity")}
    for name in ("adults", "children"):
        if name in request.query_params:
            data[name] = request.query_params[name]
    return data


@extend_schema(
    tags=["inventory"],
    parameters=ROOM_TYPE_FILTER_PARAMETERS,
    responses={
        status.HTTP_200_OK: RoomTypeSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE,
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def room_type_list(request: Request) -> Response:
    """Return all public room categories, optionally filtered by capacity and amenities."""

    filters = RoomTypeFilterSerializer(data=room_type_filter_data(request))
    filters.is_valid(raise_exception=True)

    room_types = room_type_queryset()
    adults = filters.validated_data.get("adults")
    children = filters.validated_data.get("children")
    if adults is not None:
        room_types = room_types.filter(max_adults__gte=adults)
    if children is not None:
        room_types = room_types.filter(max_children__gte=children)
    for amenity_slug in filters.validated_data.get("amenity", []):
        room_types = room_types.filter(amenities__slug=amenity_slug)

    return Response(RoomTypeSerializer(room_types.distinct(), many=True).data)


@extend_schema(
    tags=["inventory"],
    responses={
        status.HTTP_200_OK: RoomTypeSerializer,
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSE,
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def room_type_detail(_request: Request, slug: str) -> Response:
    """Return one public category by slug without exposing physical room assignment."""

    room_type = get_object_or_404(room_type_queryset(), slug=slug)
    return Response(RoomTypeSerializer(room_type).data)
