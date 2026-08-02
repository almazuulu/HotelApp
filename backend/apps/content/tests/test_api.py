import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.content.models import HeroSlide, HotelFeature, HotelProfile


def create_profile(**overrides: object) -> HotelProfile:
    values: dict[str, object] = {
        "name": "Отель Ала-Тоо",
        "tagline": "Тихое место в центре Бишкека",
        "about_title": "Добро пожаловать в Отель Ала-Тоо",
        "about_text": "Здесь начинается спокойное путешествие.",
        "address": "ул. Токтогула, 101, Бишкек",
        "phone": "+996 312 123 456",
        "email": "stay@example.com",
        "footer_text": "Отель Ала-Тоо · спокойное бронирование.",
        "seo_title": "Отель Ала-Тоо — Бишкек",
        "seo_description": "Гостиница в центре Бишкека.",
        "seo_keywords": "отель, Бишкек",
    }
    values.update(overrides)
    return HotelProfile.objects.create(**values)


@pytest.mark.django_db
def test_site_endpoint_returns_complete_public_cms_and_only_active_blocks() -> None:
    profile = create_profile()
    HeroSlide.objects.create(
        profile=profile,
        eyebrow="В центре города",
        title="Найдите время для отдыха",
        body="Светлые номера и внимательная команда.",
        image_url="https://images.example.com/hero.jpg",
        primary_cta_label="Посмотреть номера",
        primary_cta_url="#rooms",
        secondary_cta_label="Связаться с нами",
        secondary_cta_url="#contacts",
        sort_order=2,
    )
    HeroSlide.objects.create(
        profile=profile,
        eyebrow="Скрытый",
        title="Не публикуется",
        is_active=False,
    )
    HotelFeature.objects.create(
        profile=profile,
        icon="☕",
        title="Завтрак",
        description="Начинайте день без спешки.",
        sort_order=1,
    )
    HotelFeature.objects.create(
        profile=profile,
        icon="×",
        title="Скрыто",
        description="Не публикуется.",
        is_active=False,
    )

    response = APIClient().get(reverse("api-v1:content:site-content"))

    assert response.status_code == 200
    assert response.json() == {
        "name": "Отель Ала-Тоо",
        "tagline": "Тихое место в центре Бишкека",
        "about_title": "Добро пожаловать в Отель Ала-Тоо",
        "about_text": "Здесь начинается спокойное путешествие.",
        "address": "ул. Токтогула, 101, Бишкек",
        "phone": "+996 312 123 456",
        "email": "stay@example.com",
        "check_in_time": "14:00:00",
        "check_out_time": "12:00:00",
        "footer_text": "Отель Ала-Тоо · спокойное бронирование.",
        "seo_title": "Отель Ала-Тоо — Бишкек",
        "seo_description": "Гостиница в центре Бишкека.",
        "seo_keywords": "отель, Бишкек",
        "hero_slides": [
            {
                "eyebrow": "В центре города",
                "title": "Найдите время для отдыха",
                "body": "Светлые номера и внимательная команда.",
                "image_url": "https://images.example.com/hero.jpg",
                "primary_cta_label": "Посмотреть номера",
                "primary_cta_url": "#rooms",
                "secondary_cta_label": "Связаться с нами",
                "secondary_cta_url": "#contacts",
            }
        ],
        "features": [
            {
                "icon": "☕",
                "title": "Завтрак",
                "description": "Начинайте день без спешки.",
            }
        ],
    }


@pytest.mark.django_db
def test_site_endpoint_uses_the_uniform_not_found_envelope_without_profile() -> None:
    response = APIClient().get(reverse("api-v1:content:site-content"))

    assert response.status_code == 404
    assert response.json() == {
        "code": "NOT_FOUND",
        "message": "Объект не найден.",
        "errors": None,
    }


@pytest.mark.django_db
def test_schema_publishes_the_public_site_endpoint() -> None:
    response = APIClient().get(f"{reverse('api-v1:schema')}?format=json")

    assert response.status_code == 200
    schema = json.loads(response.content)
    assert "/api/v1/site/" in schema["paths"]
    assert "SiteContent" in schema["components"]["schemas"]
