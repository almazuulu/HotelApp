"""Test-only URLs used to exercise global HTTP policy without shipping probes."""

from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
def raise_domain_error(_request):
    from config.errors import ApiErrorCode, DomainError

    raise DomainError(ApiErrorCode.ROOM_UNAVAILABLE)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def csrf_protected_write(_request):
    return Response(status=204)


urlpatterns = [
    path("domain-error/", raise_domain_error),
    path("csrf-protected-write/", csrf_protected_write),
]
