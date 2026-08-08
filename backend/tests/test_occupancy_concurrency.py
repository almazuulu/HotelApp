from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Barrier

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.inventory.models import Room, RoomOccupancy, RoomType
from apps.inventory.occupancy import RoomUnavailable, Stay, allocate

pytestmark = [
    pytest.mark.skipif(
        connection.vendor != "postgresql",
        reason="concurrent occupancy allocation requires PostgreSQL row locking",
    ),
    pytest.mark.django_db(transaction=True),
]


def create_booking(room_type: RoomType, identifier: str) -> Booking:
    customer = get_user_model().objects.create_user(
        username=f"race-{identifier}",
        email=f"race-{identifier}@example.com",
        first_name="Гонка",
        last_name="Тест",
        phone=f"+996700{identifier.zfill(6)}",
        password="test-password",
    )
    return Booking.objects.create(
        customer=customer,
        room_type=room_type,
        check_in=date(2026, 9, 10),
        check_out=date(2026, 9, 11),
        adults=1,
        children=0,
        status=BookingStatus.AWAITING_PAYMENT,
        expires_at=timezone.now() + timedelta(minutes=30),
    )


@pytest.mark.django_db(transaction=True)
def test_last_room_race_has_exactly_one_successful_allocation() -> None:
    room_type = RoomType.objects.create(
        name="Гоночный",
        slug="race",
        description="Тестовая категория.",
        price_per_night="120.00",
        max_adults=2,
        max_children=1,
        area_sqm="32.50",
        bed_count=1,
    )
    Room.objects.create(room_type=room_type, number="race-101")
    bookings = [create_booking(room_type, identifier) for identifier in ("one", "two")]
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))
    barrier = Barrier(2)

    def allocate_from_separate_connection(booking: Booking) -> str:
        close_old_connections()
        try:
            barrier.wait(timeout=5)
            allocate(room_type, stay, booking)
            return "allocated"
        except RoomUnavailable:
            return "unavailable"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(allocate_from_separate_connection, bookings))

    assert sorted(results) == ["allocated", "unavailable"]
    assert RoomOccupancy.objects.count() == 1
