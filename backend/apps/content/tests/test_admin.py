import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.accounts.models import User
from apps.content.models import HeroSlide
from apps.content.tests.test_api import create_profile


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
        content_type__app_label="content",
        codename__in={
            "view_hotelprofile",
            "change_hotelprofile",
            "view_heroslide",
            "add_heroslide",
            "change_heroslide",
            "delete_heroslide",
            "view_hotelfeature",
            "add_hotelfeature",
            "change_hotelfeature",
            "delete_hotelfeature",
        },
    )
    editor.user_permissions.add(*permissions)
    return editor


@pytest.mark.django_db
def test_content_editor_can_change_cms_but_cannot_access_customer_records(client) -> None:
    profile = create_profile()
    editor = create_content_editor()
    client.force_login(editor)

    profile_response = client.get(reverse("admin:content_hotelprofile_change", args=[profile.pk]))
    accounts_response = client.get(reverse("admin:accounts_user_changelist"))

    assert profile_response.status_code == 200
    assert accounts_response.status_code == 403


@pytest.mark.django_db
def test_content_editor_can_change_a_hero_slide(client) -> None:
    slide = HeroSlide.objects.create(
        profile=create_profile(),
        eyebrow="Тест",
        title="Hero",
    )
    client.force_login(create_content_editor())

    response = client.get(reverse("admin:content_heroslide_change", args=[slide.pk]))

    assert response.status_code == 200
