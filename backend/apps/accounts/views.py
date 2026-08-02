"""Thin HTTP entry points for the session-authenticated account API."""

from django.contrib.auth import login, logout
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import (
    DetailSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
    UserSerializer,
)

ERROR_RESPONSE = OpenApiResponse(response={"$ref": "#/components/schemas/ApiError"})


@extend_schema(
    tags=["accounts"],
    request=RegistrationSerializer,
    responses={
        status.HTTP_201_CREATED: UserSerializer,
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE,
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request: Request) -> Response:
    """Register a customer and begin their Django session."""

    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    login(request, user)
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["accounts"],
    request=LoginSerializer,
    responses={
        status.HTTP_200_OK: UserSerializer,
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE,
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSE,
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request: Request) -> Response:
    """Create a session from username and password."""

    serializer = LoginSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    login(request, user)
    return Response(UserSerializer(user).data)


@extend_schema(
    tags=["accounts"],
    request=None,
    responses={
        status.HTTP_204_NO_CONTENT: None,
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSE,
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request: Request) -> Response:
    """End the current customer's session."""

    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["accounts"],
    request=UserSerializer,
    responses={
        status.HTTP_200_OK: UserSerializer,
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE,
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSE,
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSE,
    },
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    """Read or update only the profile belonging to the current session."""

    if request.method == "GET":
        return Response(UserSerializer(request.user).data)

    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializer(user).data)


@extend_schema(
    tags=["accounts"],
    request=PasswordResetRequestSerializer,
    responses={
        status.HTTP_200_OK: DetailSerializer,
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE,
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request: Request) -> Response:
    """Request a password reset without disclosing whether the email exists."""

    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"detail": "Если аккаунт существует, письмо для сброса уже отправлено."})


@extend_schema(
    tags=["accounts"],
    request=PasswordResetConfirmSerializer,
    responses={
        status.HTTP_200_OK: DetailSerializer,
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSE,
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSE,
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request: Request) -> Response:
    """Set a new password after a valid standard Django token is supplied."""

    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"detail": "Пароль изменён. Теперь войдите с новым паролем."})
