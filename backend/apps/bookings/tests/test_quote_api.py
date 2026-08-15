from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.stay_policy import BOOKING_HORIZON_DAYS, CHECK_IN_CUTOFF, validate_stay
from apps.inventory.models import Room, RoomType
from apps.inventory.occupancy import Stay, allocate
from config.errors import DomainError

pytestmark = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="quote availability requires the PostgreSQL occupancy ledger",
)


def create_room_type(**overrides: object) -> RoomType:
    values: dict[str, object] = {
        "name": "Делюкс",
        "slug": "deluxe",
        "description": "Просторный номер.",
        "price_per_night": Decimal("120.00"),
        "max_adults": 2,
        "max_children": 1,
        "area_sqm": Decimal("32.50"),
        "bed_count": 1,
        "confirmation_mode": "automatic",
    }
    values.update(overrides)
    return RoomType.objects.create(**values)


def quote_payload(**overrides: object) -> dict[str, object]:
    check_in = timezone.localdate() + timedelta(days=2)
    values: dict[str, object] = {
        "check_in": check_in.isoformat(),
        "check_out": (check_in + timedelta(days=3)).isoformat(),
        "room_type": "deluxe",
        "adults": 2,
        "children": 1,
    }
    values.update(overrides)
    return values


def create_booking(room_type: RoomType, **overrides: object) -> Booking:
    check_in = timezone.localdate() + timedelta(days=2)
    values: dict[str, object] = {
        "customer": get_user_model().objects.create_user(
            username=f"guest-{Booking.objects.count()}",
            email=f"guest-{Booking.objects.count()}@example.com",
            first_name="Guest",
            last_name="User",
            phone="+996700000000",
            password="safe-password-123",
        ),
        "room_type": room_type,
        "check_in": check_in,
        "check_out": check_in + timedelta(days=3),
        "adults": 2,
        "children": 0,
        "status": BookingStatus.PAID,
        "expires_at": None,
    }
    values.update(overrides)
    return Booking.objects.create(**values)


def allocate_booking(booking: Booking) -> None:
    allocate(
        booking.room_type,
        Stay(check_in=booking.check_in, check_out=booking.check_out),
        booking,
    )


@pytest.mark.django_db
def test_quote_returns_available_authoritative_decimal_price_without_creating_a_booking() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="101")

    response = APIClient().post(
        reverse("api-v1:bookings:quote"),
        quote_payload(),
        format="json",
    )

    assert response.status_code == 200
    assert response.json() == {
        "available": True,
        "nights": 3,
        "price_per_night": "120.00",
        "total": "360.00",
    }
    assert Booking.objects.count() == 0


@pytest.mark.django_db
def test_quote_reports_unavailable_when_every_physical_room_is_occupied() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="101")
    allocate_booking(create_booking(room_type))

    response = APIClient().post(
        reverse("api-v1:bookings:quote"),
        quote_payload(),
        format="json",
    )

    assert response.status_code == 200
    assert response.json() == {
        "available": False,
        "nights": 3,
        "price_per_night": "120.00",
        "total": "360.00",
    }


@pytest.mark.django_db
def test_quote_treats_stays_as_half_open_intervals() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="101")
    requested_check_in = timezone.localdate() + timedelta(days=2)
    allocate_booking(create_booking(
        room_type,
        check_in=requested_check_in - timedelta(days=1),
        check_out=requested_check_in,
    ))

    response = APIClient().post(
        reverse("api-v1:bookings:quote"),
        quote_payload(),
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["available"] is True


@pytest.mark.django_db
def test_quote_uses_the_ledger_to_release_expired_holds() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="101")
    expired = create_booking(
        room_type,
        status=BookingStatus.PENDING_CONFIRMATION,
        expires_at=timezone.now() - timedelta(minutes=1),
    )
    allocate_booking(expired)

    response = APIClient().post(
        reverse("api-v1:bookings:quote"),
        quote_payload(),
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["available"] is True
    expired.refresh_from_db()
    assert expired.status == BookingStatus.PENDING_CONFIRMATION
    assert expired.expires_at is not None


@pytest.mark.django_db
def test_quote_uses_uniform_errors_for_invalid_request_and_stay_window() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="101")
    client = APIClient()

    invalid_request = client.post(
        reverse("api-v1:bookings:quote"),
        quote_payload(adults=0),
        format="json",
    )
    invalid_stay = client.post(
        reverse("api-v1:bookings:quote"),
        quote_payload(check_out=quote_payload()["check_in"]),
        format="json",
    )

    assert invalid_request.status_code == 400
    assert invalid_request.json()["code"] == "VALIDATION_ERROR"
    assert invalid_stay.status_code == 400
    assert invalid_stay.json()["code"] == "STAY_WINDOW_INVALID"


@pytest.mark.django_db
def test_quote_returns_not_found_for_an_unknown_room_type() -> None:
    response = APIClient().post(
        reverse("api-v1:bookings:quote"),
        quote_payload(room_type="missing"),
        format="json",
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("adults", "children"),
    [(3, 0), (1, 2)],
)
def test_quote_checks_adult_and_child_capacity_independently(adults: int, children: int) -> None:
    room_type = create_room_type(max_adults=2, max_children=1)
    Room.objects.create(room_type=room_type, number="101")

    response = APIClient().post(
        reverse("api-v1:bookings:quote"),
        quote_payload(adults=adults, children=children),
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["available"] is False


@pytest.mark.parametrize(
    "check_in, check_out",
    [
        (timezone.localdate() + timedelta(days=1), timezone.localdate() + timedelta(days=1)),
        (
            timezone.localdate() + timedelta(days=1),
            timezone.localdate() + timedelta(days=32),
        ),
        (
            timezone.localdate() + timedelta(days=BOOKING_HORIZON_DAYS + 1),
            timezone.localdate() + timedelta(days=BOOKING_HORIZON_DAYS + 2),
        ),
    ],
)
def test_stay_policy_rejects_invalid_lengths_and_horizon(check_in, check_out) -> None:
    with pytest.raises(DomainError) as error:
        validate_stay(check_in, check_out, timezone.now())

    assert error.value.code == "STAY_WINDOW_INVALID"


@pytest.mark.parametrize("nights", [1, 30])
def test_stay_policy_accepts_the_minimum_and_maximum_stay_lengths(nights: int) -> None:
    check_in = timezone.localdate() + timedelta(days=1)

    stay = validate_stay(check_in, check_in + timedelta(days=nights), timezone.now())

    assert stay.nights == nights


def test_stay_policy_accepts_the_last_day_of_the_booking_horizon() -> None:
    check_in = timezone.localdate() + timedelta(days=BOOKING_HORIZON_DAYS)

    stay = validate_stay(check_in, check_in + timedelta(days=1), timezone.now())

    assert stay.check_in == check_in


def test_stay_policy_rejects_same_day_check_in_after_cutoff() -> None:
    today = timezone.localdate()
    now = timezone.make_aware(datetime.combine(today, CHECK_IN_CUTOFF))

    with pytest.raises(DomainError) as error:
        validate_stay(today, today + timedelta(days=1), now)

    assert error.value.code == "STAY_WINDOW_INVALID"


def test_stay_policy_accepts_same_day_check_in_before_cutoff() -> None:
    today = timezone.localdate()
    now = timezone.make_aware(datetime.combine(today, CHECK_IN_CUTOFF) - timedelta(minutes=1))

    stay = validate_stay(today, today + timedelta(days=1), now)

    assert stay.nights == 1


@pytest.mark.django_db
def test_schema_publishes_the_quote_endpoint_and_decimal_totals() -> None:
    response = APIClient().get(f"{reverse('api-v1:schema')}?format=json")

    assert response.status_code == 200
    quote_operation = response.json()["paths"]["/api/v1/quotes/"]["post"]
    quote_schema = quote_operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert quote_schema["$ref"].endswith("/Quote")
