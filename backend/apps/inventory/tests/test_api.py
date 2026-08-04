import json
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.inventory.models import Amenity, Room, RoomType, RoomTypeImage


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
        "confirmation_mode": "automatic",
    }
    values.update(overrides)
    return RoomType.objects.create(**values)


@pytest.mark.django_db
def test_room_type_list_returns_complete_customer_safe_dto_without_pagination() -> None:
    room_type = create_room_type()
    breakfast = Amenity.objects.create(name="Завтрак", slug="breakfast")
    wifi = Amenity.objects.create(name="Wi-Fi", slug="wifi")
    room_type.amenities.add(wifi, breakfast)
    RoomTypeImage.objects.create(
        room_type=room_type,
        image_url="https://images.example.com/deluxe-main.jpg",
        alt_text="Делюкс с двуспальной кроватью",
        sort_order=1,
    )
    RoomTypeImage.objects.create(
        room_type=room_type,
        image_url="https://images.example.com/deluxe-window.jpg",
        alt_text="Окно номера делюкс",
        sort_order=0,
    )
    Room.objects.create(room_type=room_type, number="007")

    response = APIClient().get(reverse("api-v1:inventory:room-type-list"))

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Делюкс",
            "slug": "deluxe",
            "description": "Просторный номер с видом на город.",
            "price_per_night": "120.00",
            "max_adults": 2,
            "max_children": 1,
            "area_sqm": "32.50",
            "bed_count": 1,
            "confirmation_mode": "automatic",
            "amenities": [
                {"name": "Wi-Fi", "slug": "wifi"},
                {"name": "Завтрак", "slug": "breakfast"},
            ],
            "images": [
                {
                    "image_url": "https://images.example.com/deluxe-window.jpg",
                    "alt_text": "Окно номера делюкс",
                },
                {
                    "image_url": "https://images.example.com/deluxe-main.jpg",
                    "alt_text": "Делюкс с двуспальной кроватью",
                },
            ],
        }
    ]
    assert "007" not in response.content.decode()
    assert "id" not in response.json()[0]


@pytest.mark.django_db
def test_room_type_detail_returns_one_category_by_slug() -> None:
    room_type = create_room_type(confirmation_mode="manual")

    response = APIClient().get(
        reverse("api-v1:inventory:room-type-detail", kwargs={"slug": room_type.slug})
    )

    assert response.status_code == 200
    assert response.json()["slug"] == "deluxe"
    assert response.json()["confirmation_mode"] == "manual"


@pytest.mark.django_db
def test_capacity_filters_are_independent() -> None:
    create_room_type(name="Семейный", slug="family", max_adults=2, max_children=3)
    create_room_type(
        name="Для взрослых",
        slug="adults-only",
        max_adults=4,
        max_children=0,
    )

    client = APIClient()
    adults_response = client.get(reverse("api-v1:inventory:room-type-list"), {"adults": 3})
    children_response = client.get(reverse("api-v1:inventory:room-type-list"), {"children": 2})

    assert [item["slug"] for item in adults_response.json()] == ["adults-only"]
    assert [item["slug"] for item in children_response.json()] == ["family"]


@pytest.mark.django_db
def test_amenity_filter_requires_every_repeated_slug_and_unknown_slug_is_empty() -> None:
    breakfast = Amenity.objects.create(name="Завтрак", slug="breakfast")
    wifi = Amenity.objects.create(name="Wi-Fi", slug="wifi")
    deluxe = create_room_type()
    deluxe.amenities.add(breakfast, wifi)
    basic = create_room_type(name="Стандарт", slug="standard")
    basic.amenities.add(wifi)

    client = APIClient()
    matching_response = client.get(
        f"{reverse('api-v1:inventory:room-type-list')}?amenity=wifi&amenity=breakfast"
    )
    unknown_response = client.get(
        f"{reverse('api-v1:inventory:room-type-list')}?amenity=not-present"
    )

    assert [item["slug"] for item in matching_response.json()] == ["deluxe"]
    assert unknown_response.json() == []


@pytest.mark.django_db
@pytest.mark.parametrize("query", [{"adults": 0}, {"adults": "two"}, {"children": -1}])
def test_invalid_catalog_filters_use_the_uniform_validation_error(query: dict[str, object]) -> None:
    response = APIClient().get(reverse("api-v1:inventory:room-type-list"), query)

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.json()["errors"]


@pytest.mark.django_db
def test_missing_room_type_slug_uses_the_uniform_not_found_envelope() -> None:
    response = APIClient().get(
        reverse("api-v1:inventory:room-type-detail", kwargs={"slug": "not-present"})
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "NOT_FOUND",
        "message": "Объект не найден.",
        "errors": None,
    }


@pytest.mark.django_db
def test_schema_publishes_room_type_paths_filters_and_confirmation_mode_enum() -> None:
    response = APIClient().get(f"{reverse('api-v1:schema')}?format=json")

    assert response.status_code == 200
    schema = json.loads(response.content)
    list_path = schema["paths"]["/api/v1/room-types/"]["get"]
    assert {parameter["name"] for parameter in list_path["parameters"]} == {
        "adults",
        "children",
        "amenity",
    }
    assert "/api/v1/room-types/{slug}/" in schema["paths"]

    confirmation_mode = schema["components"]["schemas"]["RoomType"]["properties"][
        "confirmation_mode"
    ]
    mode_reference = confirmation_mode.get("$ref") or confirmation_mode["allOf"][0]["$ref"]
    mode_name = mode_reference.rsplit("/", maxsplit=1)[-1]
    assert schema["components"]["schemas"][mode_name]["enum"] == ["automatic", "manual"]
