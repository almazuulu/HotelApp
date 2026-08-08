from decimal import Decimal

import pytest
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError

from apps.inventory.models import Amenity, Room, RoomOccupancy, RoomType, RoomTypeImage


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


@pytest.mark.django_db
def test_catalog_slug_and_physical_room_number_are_unique() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="007")

    with transaction.atomic():
        with pytest.raises(IntegrityError):
            create_room_type(name="Другой", slug=room_type.slug)
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            Room.objects.create(room_type=room_type, number="007")

    assert Room.objects.get(number="007").number == "007"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("price_per_night", Decimal("0.00")),
        ("area_sqm", Decimal("0.00")),
        ("max_adults", 0),
        ("max_children", -1),
        ("bed_count", 0),
    ],
)
def test_room_type_database_constraints_reject_invalid_catalog_values(
    field: str, value: Decimal | int
) -> None:
    with pytest.raises(IntegrityError):
        create_room_type(**{field: value})


@pytest.mark.django_db
def test_room_type_uses_decimal_values_without_float_conversion() -> None:
    room_type = create_room_type(
        price_per_night=Decimal("99.95"),
        area_sqm=Decimal("29.75"),
    )
    room_type.refresh_from_db()

    assert room_type.price_per_night == Decimal("99.95")
    assert room_type.area_sqm == Decimal("29.75")


@pytest.mark.django_db
def test_room_type_cannot_be_deleted_while_a_physical_room_exists() -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="010")

    with pytest.raises(ProtectedError):
        room_type.delete()


@pytest.mark.django_db
def test_catalog_and_gallery_ordering_are_deterministic() -> None:
    deluxe = create_room_type()
    create_room_type(name="Апартаменты", slug="suite")
    first = RoomTypeImage.objects.create(
        room_type=deluxe,
        image_url="https://images.example.com/deluxe-first.jpg",
        alt_text="Первое фото",
        sort_order=1,
    )
    second = RoomTypeImage.objects.create(
        room_type=deluxe,
        image_url="https://images.example.com/deluxe-second.jpg",
        alt_text="Второе фото",
        sort_order=1,
    )
    RoomTypeImage.objects.create(
        room_type=deluxe,
        image_url="https://images.example.com/deluxe-zero.jpg",
        alt_text="Нулевое фото",
        sort_order=0,
    )

    assert list(RoomType.objects.values_list("slug", flat=True)) == ["suite", "deluxe"]
    assert list(deluxe.images.values_list("pk", flat=True)) == [
        deluxe.images.get(sort_order=0).pk,
        first.pk,
        second.pk,
    ]


@pytest.mark.django_db
def test_amenities_are_sorted_by_name() -> None:
    Amenity.objects.create(name="Wi-Fi", slug="wifi")
    Amenity.objects.create(name="Завтрак", slug="breakfast")

    assert list(Amenity.objects.values_list("slug", flat=True)) == ["wifi", "breakfast"]


@pytest.mark.django_db
@pytest.mark.skipif(
    connection.vendor != "sqlite",
    reason="the PostgreSQL suite intentionally creates RoomOccupancy",
)
def test_room_occupancy_table_is_not_created_for_the_sqlite_suite() -> None:
    assert RoomOccupancy._meta.db_table not in connection.introspection.table_names()
