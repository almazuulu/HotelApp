from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.inventory.models import Room, RoomType


def create_user(identifier: str):
    return get_user_model().objects.create_user(
        username=f"customer-{identifier}",
        email=f"customer-{identifier}@example.com",
        first_name="Customer",
        last_name="Test",
        phone=f"+996555{identifier.zfill(6)}",
        password="test-password",
    )


def create_room_type() -> RoomType:
    return RoomType.objects.create(
        name="Делюкс",
        slug="deluxe",
        description="Просторный номер.",
        price_per_night="120.00",
        max_adults=2,
        max_children=1,
        area_sqm="32.50",
        bed_count=1,
    )


def create_booking(customer, room_type: RoomType, **overrides: object) -> Booking:
    today = timezone.localdate()
    values: dict[str, object] = {
        "customer": customer,
        "room_type": room_type,
        "check_in": today + timedelta(days=5),
        "check_out": today + timedelta(days=7),
        "adults": 2,
        "children": 1,
        "status": BookingStatus.AWAITING_PAYMENT,
        "expires_at": timezone.now() + timedelta(minutes=30),
        "cancellable_until": timezone.now() + timedelta(days=2),
    }
    values.update(overrides)
    return Booking.objects.create(**values)


def authenticated_client(customer) -> APIClient:
    client = APIClient()
    client.force_authenticate(customer)
    return client


@pytest.mark.django_db
def test_booking_list_separates_active_and_history_without_physical_room_data() -> None:
    customer = create_user("list")
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="101")
    active = create_booking(customer, room_type)
    historic = create_booking(
        customer,
        room_type,
        check_in=timezone.localdate() - timedelta(days=4),
        check_out=timezone.localdate() - timedelta(days=2),
    )

    response = authenticated_client(customer).get(reverse("api-v1:bookings:booking-list"))

    assert response.status_code == 200
    assert [item["reference"] for item in response.json()["active"]] == [str(active.reference)]
    assert [item["reference"] for item in response.json()["history"]] == [str(historic.reference)]
    public_booking = response.json()["active"][0]
    assert public_booking["room_type"] == "deluxe"
    assert "id" not in public_booking
    assert "room" not in public_booking
    assert "occupancy" not in public_booking
    assert "101" not in response.content.decode()


@pytest.mark.django_db
def test_booking_list_puts_terminal_statuses_in_history_without_completed_status() -> None:
    customer = create_user("terminal")
    room_type = create_room_type()
    rejected = create_booking(
        customer,
        room_type,
        status=BookingStatus.REJECTED,
        expires_at=None,
    )

    response = authenticated_client(customer).get(reverse("api-v1:bookings:booking-list"))

    assert response.status_code == 200
    assert response.json()["active"] == []
    assert [item["reference"] for item in response.json()["history"]] == [str(rejected.reference)]
    assert "completed" not in response.content.decode()


@pytest.mark.django_db
def test_booking_detail_is_visible_only_to_its_owner() -> None:
    owner = create_user("owner")
    other_customer = create_user("other")
    booking = create_booking(owner, create_room_type())
    detail_url = reverse("api-v1:bookings:booking-detail", kwargs={"reference": booking.reference})

    owner_response = authenticated_client(owner).get(detail_url)
    other_response = authenticated_client(other_customer).get(detail_url)

    assert owner_response.status_code == 200
    assert owner_response.json()["reference"] == str(booking.reference)
    assert other_response.status_code == 404
    assert other_response.json()["code"] == "NOT_FOUND"


@pytest.mark.django_db
def test_booking_endpoints_return_the_uniform_error_for_anonymous_users() -> None:
    room_type = create_room_type()
    booking = create_booking(create_user("anonymous-owner"), room_type)
    client = APIClient()

    list_response = client.get(reverse("api-v1:bookings:booking-list"))
    detail_response = client.get(
        reverse("api-v1:bookings:booking-detail", kwargs={"reference": booking.reference})
    )
    cancel_response = client.post(
        reverse("api-v1:bookings:booking-cancel", kwargs={"reference": booking.reference})
    )

    for response in (list_response, detail_response, cancel_response):
        assert response.status_code == 401
        assert response.json()["code"] == "NOT_AUTHENTICATED"


@pytest.mark.django_db
def test_stale_hold_expires_before_detail_is_serialized(monkeypatch) -> None:
    customer = create_user("stale")
    booking = create_booking(
        customer,
        create_room_type(),
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    release = Mock()
    monkeypatch.setattr("apps.inventory.occupancy.release", release)

    response = authenticated_client(customer).get(
        reverse("api-v1:bookings:booking-detail", kwargs={"reference": booking.reference})
    )

    assert response.status_code == 200
    assert response.json()["status"] == BookingStatus.EXPIRED
    assert response.json()["hold_expires_at"] is None
    booking.refresh_from_db()
    assert booking.status == BookingStatus.EXPIRED
    assert booking.expires_at is None
    release.assert_called_once_with(booking)


@pytest.mark.django_db
def test_stale_hold_expires_before_list_is_serialized(monkeypatch) -> None:
    customer = create_user("stale-list")
    booking = create_booking(
        customer,
        create_room_type(),
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    release = Mock()
    monkeypatch.setattr("apps.inventory.occupancy.release", release)

    response = authenticated_client(customer).get(reverse("api-v1:bookings:booking-list"))

    assert response.status_code == 200
    assert response.json()["active"] == []
    assert response.json()["history"][0]["status"] == BookingStatus.EXPIRED
    booking.refresh_from_db()
    assert booking.status == BookingStatus.EXPIRED
    release.assert_called_once_with(booking)


@pytest.mark.django_db
def test_customer_can_cancel_only_their_own_booking(monkeypatch) -> None:
    customer = create_user("cancel")
    other_customer = create_user("cancel-other")
    booking = create_booking(customer, create_room_type())
    release = Mock()
    monkeypatch.setattr("apps.inventory.occupancy.release", release)
    cancel_url = reverse("api-v1:bookings:booking-cancel", kwargs={"reference": booking.reference})

    other_response = authenticated_client(other_customer).post(cancel_url)
    owner_response = authenticated_client(customer).post(cancel_url)

    assert other_response.status_code == 404
    assert owner_response.status_code == 200
    assert owner_response.json()["status"] == BookingStatus.CANCELLED
    booking.refresh_from_db()
    assert booking.status == BookingStatus.CANCELLED
    assert booking.expires_at is None
    release.assert_called_once_with(booking)


@pytest.mark.django_db
def test_customer_cannot_cancel_a_paid_booking(monkeypatch) -> None:
    customer = create_user("paid-cancel")
    booking = create_booking(
        customer,
        create_room_type(),
        status=BookingStatus.PAID,
        expires_at=None,
    )
    release = Mock()
    monkeypatch.setattr("apps.inventory.occupancy.release", release)

    response = authenticated_client(customer).post(
        reverse("api-v1:bookings:booking-cancel", kwargs={"reference": booking.reference})
    )

    assert response.status_code == 409
    assert response.json()["code"] == "TRANSITION_NOT_ALLOWED"
    release.assert_not_called()
