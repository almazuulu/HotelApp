"""Thin read-only HTTP entry point for public hotel content."""

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .models import HeroSlide, HotelFeature, HotelProfile
from .serializers import SiteContentSerializer

ERROR_RESPONSE = OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"})


@extend_schema(
    tags=["site"],
    responses={
        status.HTTP_200_OK: SiteContentSerializer,
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSE,
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def site_content(_request: Request) -> Response:
    """Return the complete fixed CMS document for the one hotel."""

    profile = get_object_or_404(
        HotelProfile.objects.prefetch_related(
            Prefetch("hero_slides", queryset=HeroSlide.objects.filter(is_active=True)),
            Prefetch("features", queryset=HotelFeature.objects.filter(is_active=True)),
        ),
        pk=1,
    )
    return Response(SiteContentSerializer(profile).data)
