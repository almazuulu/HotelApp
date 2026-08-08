from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import (
    TERMINAL_BOOKING_STATUSES,
    Booking,
    BookingStatus,
)
from apps.inventory.models import RoomType


def create_customer(**overrides: object) -> User:
    values: dict[str, object] = {
        "username": "customer",
        "email": "customer@example.com",
        "first_name": "Иван",
        "last_name": "Иванов",
        "phone": "+996555000000",
    }
    values.update(overrides)
    return User.objects.create(**values)


def create_room_type(**overrides: object) -> RoomType:
    values: dict[str, object] = {
        "name": "Делюкс",
        "slug": "deluxe",
        "description": "Просторный номер с видом на город.",
        "price_per_night": Decimal("120.00"),
        "max_adults": 2,
        "max_children": 1,
        "area_sqm": Decimal("32.50"),
        "bed_count": 1,
    }
    values.update(overrides)
    return RoomType.objects.create(**values)


def create_booking(**overrides: object) -> Booking:
    check_in = date(2026, 9, 10)
    customer = overrides.pop("customer", None)
    room_type = overrides.pop("room_type", None)
    values: dict[str, object] = {
        "customer": create_customer() if customer is None else customer,
        "room_type": create_room_type() if room_type is None else room_type,
        "check_in": check_in,
        "check_out": date(2026, 9, 11),
        "adults": 1,
        "children": 0,
        "status": BookingStatus.AWAITING_PAYMENT,
        "expires_at": timezone.make_aware(datetime(2026, 9, 9, 12, 0)),
    }
    values.update(overrides)
    return Booking.objects.create(**values)


@pytest.mark.django_db
def test_booking_generates_a_unique_uuid_reference() -> None:
    booking = create_booking()
    other = create_booking(
        customer=create_customer(username="other", email="other@example.com"),
        room_type=create_room_type(name="Люкс", slug="suite"),
    )

    assert isinstance(booking.reference, UUID)
    assert booking.reference != other.reference


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("check_out", date(2026, 9, 10)),
        ("check_out", date(2026, 9, 9)),
        ("adults", 0),
        ("children", -1),
        ("status", "unknown"),
    ],
)
def test_booking_database_constraints_reject_invalid_values(
    field: str, value: date | int | str
) -> None:
    with pytest.raises(IntegrityError):
        create_booking(**{field: value})


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [BookingStatus.PENDING_CONFIRMATION, BookingStatus.AWAITING_PAYMENT],
)
def test_active_booking_statuses_require_an_expiry(status: BookingStatus) -> None:
    with pytest.raises(IntegrityError):
        create_booking(status=status, expires_at=None)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [BookingStatus.PENDING_CONFIRMATION, BookingStatus.AWAITING_PAYMENT],
)
def test_active_booking_statuses_allow_an_expiry(status: BookingStatus) -> None:
    booking = create_booking(status=status)

    assert booking.expires_at is not None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        BookingStatus.PAID,
        BookingStatus.REJECTED,
        BookingStatus.CANCELLED,
        BookingStatus.EXPIRED,
    ],
)
def test_non_expiring_booking_statuses_reject_an_expiry(status: BookingStatus) -> None:
    with pytest.raises(IntegrityError):
        create_booking(status=status)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        BookingStatus.PAID,
        BookingStatus.REJECTED,
        BookingStatus.CANCELLED,
        BookingStatus.EXPIRED,
    ],
)
def test_non_expiring_booking_statuses_allow_a_null_expiry(status: BookingStatus) -> None:
    booking = create_booking(status=status, expires_at=None)

    assert booking.status == status


def test_paid_is_not_a_terminal_booking_status() -> None:
    assert TERMINAL_BOOKING_STATUSES == (
        BookingStatus.REJECTED,
        BookingStatus.CANCELLED,
        BookingStatus.EXPIRED,
    )


def test_booking_does_not_contain_a_physical_room() -> None:
    assert "room" not in {field.name for field in Booking._meta.get_fields()}
