from decimal import Decimal

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.accounts.models import User
from apps.inventory.models import Amenity, Room, RoomType, RoomTypeImage


def create_room_type() -> RoomType:
    return RoomType.objects.create(
        name="Делюкс",
        slug="deluxe",
        description="Просторный номер с видом на город.",
        price_per_night=Decimal("120.00"),
        max_adults=2,
        max_children=1,
        area_sqm=Decimal("32.50"),
        bed_count=1,
        confirmation_mode="automatic",
    )


def create_content_editor() -> User:
    editor = User.objects.create_user(
        username="editor",
        email="editor@example.com",
        first_name="Контент",
        last_name="Редактор",
        phone="+996700000001",
        password="correct-horse-battery-staple",
        is_staff=True,
    )
    permissions = Permission.objects.filter(
        content_type__app_label="inventory",
        codename__in={
            "view_amenity",
            "add_amenity",
            "change_amenity",
            "delete_amenity",
            "view_roomtype",
            "change_roomtype",
            "view_roomtypeimage",
            "add_roomtypeimage",
            "change_roomtypeimage",
            "delete_roomtypeimage",
        },
    )
    editor.user_permissions.add(*permissions)
    return editor


@pytest.mark.django_db
def test_manager_sees_full_catalog_including_physical_rooms(client) -> None:
    manager = User.objects.create_superuser(
        username="manager",
        email="manager@example.com",
        first_name="Отель",
        last_name="Менеджер",
        phone="+996700000002",
        password="correct-horse-battery-staple",
    )
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="007")
    client.force_login(manager)

    room_type_response = client.get(reverse("admin:inventory_roomtype_change", args=[room_type.pk]))
    room_response = client.get(reverse("admin:inventory_room_changelist"))

    assert room_type_response.status_code == 200
    assert b'name="price_per_night"' in room_type_response.content
    assert room_response.status_code == 200
    assert b"007" in room_response.content


@pytest.mark.django_db
def test_content_editor_can_manage_marketing_fields_amenities_and_gallery_not_commercial_fields(
    client,
) -> None:
    room_type = create_room_type()
    amenity = Amenity.objects.create(name="Завтрак", slug="breakfast")
    client.force_login(create_content_editor())
    change_url = reverse("admin:inventory_roomtype_change", args=[room_type.pk])

    get_response = client.get(change_url)
    post_response = client.post(
        change_url,
        {
            "name": "Делюкс с видом",
            "slug": "deluxe-view",
            "description": "Обновлённое маркетинговое описание.",
            "area_sqm": "35.50",
            "bed_count": "2",
            "amenities": [str(amenity.pk)],
            "price_per_night": "999.99",
            "max_adults": "99",
            "max_children": "99",
            "confirmation_mode": "manual",
            "images-TOTAL_FORMS": "1",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            "images-0-image_url": "https://images.example.com/deluxe-view.jpg",
            "images-0-alt_text": "Номер делюкс с видом на город",
            "images-0-sort_order": "0",
            "_save": "Сохранить",
        },
    )

    assert get_response.status_code == 200
    assert b'name="price_per_night"' not in get_response.content
    assert b'name="max_adults"' not in get_response.content
    assert b'name="max_children"' not in get_response.content
    assert b'name="confirmation_mode"' not in get_response.content
    assert post_response.status_code == 302

    room_type.refresh_from_db()
    assert room_type.name == "Делюкс с видом"
    assert room_type.price_per_night == Decimal("120.00")
    assert room_type.max_adults == 2
    assert room_type.max_children == 1
    assert room_type.confirmation_mode == "automatic"
    assert list(room_type.amenities.values_list("slug", flat=True)) == ["breakfast"]
    assert (
        RoomTypeImage.objects.get(room_type=room_type).alt_text
        == "Номер делюкс с видом на город"
    )


@pytest.mark.django_db
def test_content_editor_cannot_access_the_internal_room_list(client) -> None:
    room_type = create_room_type()
    Room.objects.create(room_type=room_type, number="007")
    client.force_login(create_content_editor())

    response = client.get(reverse("admin:inventory_room_changelist"))

    assert response.status_code == 403
