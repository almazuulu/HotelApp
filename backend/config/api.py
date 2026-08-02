"""Small API-contract endpoints that are available before feature APIs exist."""

from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(
    tags=["contract"],
    responses={
        200: inline_serializer(
            name="ApiRoot",
            fields={
                "service": serializers.CharField(),
                "version": serializers.CharField(),
            },
        ),
        400: OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"}),
        401: OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"}),
        403: OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"}),
        404: OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"}),
        409: OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"}),
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(_request):
    """Expose the versioned API entry point without introducing a feature endpoint."""

    return Response({"service": "HotelApp API", "version": "v1"})


@extend_schema(
    tags=["contract"],
    responses={
        200: inline_serializer(
            name="CsrfCookieResponse",
            fields={"detail": serializers.CharField()},
        )
    },
)
@ensure_csrf_cookie
@api_view(["GET"])
@permission_classes([AllowAny])
def csrf(_request):
    """Set Django's CSRF cookie for the session-authenticated SPA."""

    return Response({"detail": "CSRF cookie set."})
