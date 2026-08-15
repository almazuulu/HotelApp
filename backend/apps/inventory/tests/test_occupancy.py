from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.urls import reverse
from django.utils import timezone

from apps.bookings.lifecycle import cancel_booking
from apps.bookings.models import Booking, BookingStatus
from apps.inventory.models import MaintenanceBlock, Room, RoomOccupancy, RoomType
from apps.inventory.occupancy import RoomUnavailable, Stay, allocate, release, search

pytestmark = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="occupancy ledger requires PostgreSQL range and exclusion support",
)


def create_room_type(**overrides: object) -> RoomType:
    values: dict[str, object] = {
        "name": "Делюкс",
        "slug": "deluxe",
        "description": "Просторный номер с видом на город.",
        "price_per_night": "120.00",
        "max_adults": 2,
        "max_children": 1,
        "area_sqm": "32.50",
        "bed_count": 1,
    }
    values.update(overrides)
    return RoomType.objects.create(**values)


def create_user(identifier: str):
    return get_user_model().objects.create_user(
        username=f"user-{identifier}",
        email=f"user-{identifier}@example.com",
        first_name="Тест",
        last_name="Пользователь",
        phone=f"+996555{identifier.zfill(6)}",
        password="test-password",
    )


def create_booking(room_type: RoomType, identifier: str, **overrides: object) -> Booking:
    values: dict[str, object] = {
        "customer": create_user(identifier),
        "room_type": room_type,
        "check_in": date(2026, 9, 10),
        "check_out": date(2026, 9, 11),
        "adults": 1,
        "children": 0,
        "status": BookingStatus.AWAITING_PAYMENT,
        "expires_at": timezone.now() + timedelta(minutes=30),
    }
    values.update(overrides)
    return Booking.objects.create(**values)


@pytest.mark.django_db
def test_database_rejects_overlapping_occupancy_and_allows_adjacent_stays() -> None:
    room_type = create_room_type()
    room = Room.objects.create(room_type=room_type, number="101")
    first = create_booking(room_type, "one")
    second = create_booking(room_type, "two")
    third = create_booking(room_type, "three")
    first_stay = Stay(date(2026, 9, 10), date(2026, 9, 12))

    allocate(room_type, first_stay, first)

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            RoomOccupancy.objects.create(
                room=room,
                booking=second,
                stay=(date(2026, 9, 11), date(2026, 9, 13)),
            )

    allocate(room_type, Stay(date(2026, 9, 12), date(2026, 9, 14)), third)

    assert RoomOccupancy.objects.count() == 2


@pytest.mark.django_db
def test_search_filters_adult_and_child_capacity_independently() -> None:
    adults_only = create_room_type(
        name="Для взрослых",
        slug="adults-only",
        max_adults=3,
        max_children=0,
    )
    family = create_room_type(
        name="Семейный",
        slug="family",
        max_adults=1,
        max_children=2,
    )
    Room.objects.create(room_type=adults_only, number="201")
    Room.objects.create(room_type=family, number="202")
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))

    assert list(search(stay, adults=2, children=0)) == [adults_only]
    assert list(search(stay, adults=1, children=1)) == [family]


@pytest.mark.django_db
def test_maintenance_block_uses_its_selected_room_and_hides_the_category() -> None:
    room_type = create_room_type()
    room = Room.objects.create(room_type=room_type, number="301")
    maintenance_block = MaintenanceBlock.objects.create(
        room=room,
        reason="Плановая уборка",
        created_by=create_user("manager"),
    )
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))

    allocate(room_type, stay, maintenance_block)

    assert list(search(stay, adults=1, children=0)) == []
    occupancy = RoomOccupancy.objects.get()
    assert occupancy.maintenance_block == maintenance_block
    assert occupancy.booking is None


@pytest.mark.django_db
def test_allocate_makes_a_category_unavailable_and_release_is_idempotent() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="401")
    booking = create_booking(room_type, "allocated")
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))

    allocate(room_type, stay, booking)

    assert list(search(stay, adults=1, children=0)) == []

    release(booking)
    release(booking)

    assert RoomOccupancy.objects.count() == 0
    assert list(search(stay, adults=1, children=0)) == [room_type]


@pytest.mark.django_db
def test_cancelling_a_booking_releases_its_physical_room_through_the_ledger() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="451")
    booking = create_booking(room_type, "cancelled")
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))
    allocate(room_type, stay, booking)

    cancelled = cancel_booking(booking, timezone.now())

    assert cancelled.status == BookingStatus.CANCELLED
    assert RoomOccupancy.objects.count() == 0
    assert list(search(stay, adults=1, children=0)) == [room_type]


@pytest.mark.django_db
def test_search_releases_stale_booking_occupancy_without_changing_booking_status() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="501")
    booking = create_booking(room_type, "stale-search")
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))
    allocate(room_type, stay, booking)
    booking.expires_at = timezone.now() - timedelta(seconds=1)
    booking.save(update_fields=("expires_at",))

    assert list(search(stay, adults=1, children=0)) == [room_type]
    assert RoomOccupancy.objects.count() == 0
    assert Booking.objects.get(pk=booking.pk).status == BookingStatus.AWAITING_PAYMENT


@pytest.mark.django_db
def test_allocate_releases_stale_occupancy_before_assigning_the_room() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="601")
    stale_booking = create_booking(room_type, "stale-allocate")
    fresh_booking = create_booking(room_type, "fresh-allocate")
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))
    allocate(room_type, stay, stale_booking)
    stale_booking.expires_at = timezone.now() - timedelta(seconds=1)
    stale_booking.save(update_fields=("expires_at",))

    allocate(room_type, stay, fresh_booking)

    occupancy = RoomOccupancy.objects.get()
    assert occupancy.booking == fresh_booking


@pytest.mark.django_db
def test_allocate_raises_room_unavailable_when_no_room_can_be_assigned() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="701")
    allocated_booking = create_booking(room_type, "occupied")
    waiting_booking = create_booking(room_type, "waiting")
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))
    allocate(room_type, stay, allocated_booking)

    with pytest.raises(RoomUnavailable):
        allocate(room_type, stay, waiting_booking)


@pytest.mark.django_db
def test_allocate_does_not_translate_non_exclusion_integrity_errors() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="801")
    booking = create_booking(room_type, "one-holder")

    allocate(room_type, Stay(date(2026, 9, 10), date(2026, 9, 11)), booking)

    with pytest.raises(IntegrityError):
        allocate(room_type, Stay(date(2026, 9, 11), date(2026, 9, 12)), booking)


@pytest.mark.django_db
def test_room_occupancy_requires_exactly_one_holder() -> None:
    room_type = create_room_type()
    room = Room.objects.create(room_type=room_type, number="901")
    booking = create_booking(room_type, "both-holders")
    maintenance_block = MaintenanceBlock.objects.create(
        room=room,
        reason="Плановая уборка",
        created_by=create_user("both-holders-manager"),
    )

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            RoomOccupancy.objects.create(
                room=room,
                stay=(date(2026, 9, 10), date(2026, 9, 11)),
            )

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            RoomOccupancy.objects.create(
                room=room,
                booking=booking,
                maintenance_block=maintenance_block,
                stay=(date(2026, 9, 10), date(2026, 9, 11)),
            )


@pytest.mark.django_db
def test_schema_contains_the_immediate_exclusion_constraint_and_btree_gist_extension() -> None:
    table_name = RoomOccupancy._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'btree_gist'")
        extension = cursor.fetchone()
        cursor.execute(
            """
            SELECT contype, condeferrable
            FROM pg_constraint
            WHERE conrelid = %s::regclass
              AND conname = 'inventory_room_occupancy_no_overlapping_stays'
            """,
            [table_name],
        )
        constraint = cursor.fetchone()

    assert extension == ("btree_gist",)
    assert constraint == ("x", False)


@pytest.mark.django_db
def test_admin_creates_and_deletes_maintenance_blocks_through_the_ledger(client) -> None:
    manager = get_user_model().objects.create_superuser(
        username="manager",
        email="manager@example.com",
        first_name="Отель",
        last_name="Менеджер",
        phone="+996555999999",
        password="test-password",
    )
    room_type = create_room_type()
    room = Room.objects.create(room_type=room_type, number="1001")
    client.force_login(manager)

    create_response = client.post(
        reverse("admin:inventory_maintenanceblock_add"),
        {
            "room": room.pk,
            "reason": "Плановая уборка",
            "check_in": "2026-09-10",
            "check_out": "2026-09-11",
            "_save": "Сохранить",
        },
    )

    assert create_response.status_code == 302
    maintenance_block = MaintenanceBlock.objects.get()
    assert maintenance_block.created_by == manager
    assert RoomOccupancy.objects.get().maintenance_block == maintenance_block

    delete_response = client.post(
        reverse("admin:inventory_maintenanceblock_delete", args=[maintenance_block.pk]),
        {"post": "yes"},
    )

    assert delete_response.status_code == 302
    assert not RoomOccupancy.objects.exists()


@pytest.mark.django_db
def test_admin_renders_an_error_for_a_conflicting_maintenance_block(client) -> None:
    manager = get_user_model().objects.create_superuser(
        username="conflicting-manager",
        email="conflicting-manager@example.com",
        first_name="Отель",
        last_name="Менеджер",
        phone="+996555999998",
        password="test-password",
    )
    room_type = create_room_type()
    room = Room.objects.create(room_type=room_type, number="1002")
    booking = create_booking(room_type, "admin-conflict")
    stay = Stay(date(2026, 9, 10), date(2026, 9, 11))
    allocate(room_type, stay, booking)
    client.force_login(manager)

    response = client.post(
        reverse("admin:inventory_maintenanceblock_add"),
        {
            "room": room.pk,
            "reason": "Плановая уборка",
            "check_in": "2026-09-10",
            "check_out": "2026-09-11",
            "_save": "Сохранить",
        },
    )

    assert response.status_code == 200
    assert "На указанный период комната недоступна." in response.content.decode()
    assert not MaintenanceBlock.objects.exists()
    assert RoomOccupancy.objects.get().booking == booking
