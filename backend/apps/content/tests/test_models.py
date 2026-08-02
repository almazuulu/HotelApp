import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.content.models import HeroSlide, HotelProfile
from apps.content.tests.test_api import create_profile


@pytest.mark.django_db
def test_hotel_profile_is_a_database_enforced_singleton() -> None:
    create_profile()

    with pytest.raises(IntegrityError):
        create_profile(id=2, name="Второй отель")


@pytest.mark.django_db
def test_hotel_profile_rejects_a_non_singleton_identifier_before_save() -> None:
    profile = HotelProfile(id=2, name="Второй отель")

    with pytest.raises(ValidationError, match="только один профиль"):
        profile.clean()


@pytest.mark.django_db
def test_hero_slide_requires_a_link_when_its_button_text_is_provided() -> None:
    slide = HeroSlide(
        profile=create_profile(),
        eyebrow="Тест",
        title="Слайд",
        primary_cta_label="Открыть",
    )

    with pytest.raises(ValidationError, match="текст, и ссылка"):
        slide.clean()
