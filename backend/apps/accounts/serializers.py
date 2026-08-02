"""Serializers for the public account API."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import User


class UserSerializer(serializers.ModelSerializer[User]):
    """The customer-safe representation of the signed-in user."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "phone")
        read_only_fields = ("id",)


class RegistrationSerializer(serializers.ModelSerializer[User]):
    """Create an active customer account without exposing a password later."""

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone", "password")

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        user = User(
            username=attrs["username"],
            email=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
            phone=attrs["phone"],
        )
        validate_password(attrs["password"], user=user)
        return attrs

    def create(self, validated_data: dict[str, object]) -> User:
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer[User]):
    """Validate username/password credentials for Django session login."""

    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs: dict[str, str]) -> dict[str, object]:
        user = authenticate(
            request=self.context["request"],
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise AuthenticationFailed("Неверное имя пользователя или пароль.")

        attrs["user"] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer[None]):
    """Send a standard Django-token reset message when the account exists."""

    email = serializers.EmailField()

    def save(self, **_kwargs: object) -> None:
        email = self.validated_data["email"]
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user is None:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_origin = settings.FRONTEND_BASE_URL.rstrip("/")
        reset_url = f"{frontend_origin}/password-reset/confirm/{uid}/{token}"
        send_mail(
            subject="Сброс пароля HotelApp",
            message=(
                "Чтобы задать новый пароль, откройте ссылку:\n"
                f"{reset_url}\n\n"
                "Если вы не запрашивали сброс, проигнорируйте это письмо."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class PasswordResetConfirmSerializer(serializers.Serializer[User]):
    """Validate and consume a standard Django password-reset token."""

    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs: dict[str, str]) -> dict[str, object]:
        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "Ссылка для сброса пароля недействительна."}
            )

        validate_password(attrs["password"], user=user)
        attrs["user"] = user
        return attrs

    def save(self, **_kwargs: object) -> User:
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])
        return user


class DetailSerializer(serializers.Serializer[None]):
    """Schema component for endpoint acknowledgements."""

    detail = serializers.CharField()
