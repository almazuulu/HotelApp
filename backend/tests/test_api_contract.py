import json

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from config.errors import ERROR_CATALOG, ApiErrorCode


@pytest.mark.django_db
def test_api_root_is_reachable() -> None:
    response = APIClient().get(reverse("api-v1:root"))

    assert response.status_code == 200
    assert response.json() == {"service": "HotelApp API", "version": "v1"}


@pytest.mark.django_db
def test_csrf_endpoint_sets_cookie() -> None:
    response = APIClient(enforce_csrf_checks=True).get(reverse("api-v1:csrf"))

    assert response.status_code == 200
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
@override_settings(ROOT_URLCONF="tests.urls")
def test_domain_error_uses_the_uniform_envelope() -> None:
    response = APIClient().get("/domain-error/")

    assert response.status_code == 409
    assert response.json() == {
        "code": ApiErrorCode.ROOM_UNAVAILABLE,
        "message": ERROR_CATALOG[ApiErrorCode.ROOM_UNAVAILABLE].message,
        "errors": None,
    }


@pytest.mark.django_db
@override_settings(ROOT_URLCONF="tests.urls")
def test_authenticated_write_without_csrf_token_is_rejected() -> None:
    user = User.objects.create_user(
        username="customer",
        email="customer@example.com",
        first_name="Customer",
        last_name="Example",
        phone="+996700000000",
        password="correct-horse-battery-staple",
    )
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)

    response = client.post("/csrf-protected-write/", format="json")

    assert response.status_code == 403
    assert response.json()["code"] == ApiErrorCode.PERMISSION_DENIED


@pytest.mark.django_db
def test_schema_publishes_the_complete_error_catalogue() -> None:
    response = APIClient().get(f"{reverse('api-v1:schema')}?format=json")

    assert response.status_code == 200
    schema = json.loads(response.content)
    assert schema["openapi"].startswith("3.")
    assert set(schema["components"]["schemas"]["ApiErrorCode"]["enum"]) == {
        code.value for code in ERROR_CATALOG
    }
