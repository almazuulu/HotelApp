import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

from config.errors import ApiErrorCode

User = get_user_model()

REGISTER_PAYLOAD = {
    "username": "mariya",
    "email": "mariya@example.com",
    "first_name": "Мария",
    "last_name": "Иванова",
    "phone": "+996700123456",
    "password": "correct-horse-battery-staple",
}


def csrf_headers(client: APIClient) -> dict[str, str]:
    response = client.get(reverse("api-v1:csrf"))
    return {"HTTP_X_CSRFTOKEN": response.cookies["csrftoken"].value}


def create_user(**overrides: str):
    payload = REGISTER_PAYLOAD | overrides
    return User.objects.create_user(**payload)


@pytest.mark.django_db
def test_registration_creates_customer_and_starts_session() -> None:
    client = APIClient(enforce_csrf_checks=True)

    response = client.post(
        reverse("api-v1:accounts:register"),
        REGISTER_PAYLOAD,
        format="json",
        **csrf_headers(client),
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": User.objects.get(username="mariya").id,
        "username": "mariya",
        "email": "mariya@example.com",
        "first_name": "Мария",
        "last_name": "Иванова",
        "phone": "+996700123456",
    }
    assert client.get(reverse("api-v1:accounts:me")).status_code == 200
    assert not User.objects.get(username="mariya").is_staff


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("field", "value"),
    [("username", "mariya"), ("email", "mariya@example.com")],
)
def test_registration_rejects_duplicate_username_or_email(field: str, value: str) -> None:
    create_user()
    client = APIClient(enforce_csrf_checks=True)
    payload = REGISTER_PAYLOAD | {field: value}

    response = client.post(
        reverse("api-v1:accounts:register"),
        payload,
        format="json",
        **csrf_headers(client),
    )

    assert response.status_code == 400
    assert response.json()["code"] == ApiErrorCode.VALIDATION_ERROR
    assert field in response.json()["errors"]


@pytest.mark.django_db
def test_anonymous_write_requires_csrf_and_uses_the_standard_error_envelope() -> None:
    response = APIClient(enforce_csrf_checks=True).post(
        reverse("api-v1:accounts:register"), REGISTER_PAYLOAD, format="json"
    )

    assert response.status_code == 403
    assert response.json()["code"] == ApiErrorCode.PERMISSION_DENIED
    assert response.json()["errors"] is None


@pytest.mark.django_db
def test_login_logout_and_invalid_credentials() -> None:
    create_user()
    client = APIClient(enforce_csrf_checks=True)

    invalid_response = client.post(
        reverse("api-v1:accounts:login"),
        {"username": "mariya", "password": "not-the-password"},
        format="json",
        **csrf_headers(client),
    )

    assert invalid_response.status_code == 401
    assert invalid_response.json()["code"] == ApiErrorCode.NOT_AUTHENTICATED

    login_response = client.post(
        reverse("api-v1:accounts:login"),
        {"username": "mariya", "password": REGISTER_PAYLOAD["password"]},
        format="json",
        **csrf_headers(client),
    )

    assert login_response.status_code == 200
    assert client.get(reverse("api-v1:accounts:me")).json()["username"] == "mariya"

    logout_response = client.post(
        reverse("api-v1:accounts:logout"), format="json", **csrf_headers(client)
    )

    assert logout_response.status_code == 204
    assert client.get(reverse("api-v1:accounts:me")).status_code == 401


@pytest.mark.django_db
def test_customer_can_update_only_their_own_profile() -> None:
    first_user = create_user()
    second_user = create_user(
        username="alina",
        email="alina@example.com",
        first_name="Алина",
        last_name="Петрова",
        phone="+996700000000",
    )
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(first_user)

    response = client.patch(
        reverse("api-v1:accounts:me"),
        {"first_name": "Маша", "phone": "+996555123456"},
        format="json",
        **csrf_headers(client),
    )

    assert response.status_code == 200
    first_user.refresh_from_db()
    second_user.refresh_from_db()
    assert first_user.first_name == "Маша"
    assert first_user.phone == "+996555123456"
    assert second_user.first_name == "Алина"
    assert second_user.phone == "+996700000000"


@pytest.mark.django_db
def test_password_reset_uses_a_standard_django_token_and_changes_the_password() -> None:
    user = create_user()
    client = APIClient(enforce_csrf_checks=True)

    request_response = client.post(
        reverse("api-v1:accounts:password-reset"),
        {"email": user.email},
        format="json",
        **csrf_headers(client),
    )

    assert request_response.status_code == 200
    assert len(mail.outbox) == 1
    match = re.search(r"password-reset/confirm/([^/\s]+)/([^/\s]+)", mail.outbox[0].body)
    assert match is not None

    confirm_response = client.post(
        reverse("api-v1:accounts:password-reset-confirm"),
        {"uid": match.group(1), "token": match.group(2), "password": "a-new-safe-password"},
        format="json",
        **csrf_headers(client),
    )

    assert confirm_response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("a-new-safe-password")

    reused_token_response = client.post(
        reverse("api-v1:accounts:password-reset-confirm"),
        {"uid": match.group(1), "token": match.group(2), "password": "another-safe-password"},
        format="json",
        **csrf_headers(client),
    )

    assert reused_token_response.status_code == 400
    assert reused_token_response.json()["code"] == ApiErrorCode.VALIDATION_ERROR


@pytest.mark.django_db
def test_customers_cannot_access_django_admin() -> None:
    user = create_user()
    client = APIClient()
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("admin:login"))
