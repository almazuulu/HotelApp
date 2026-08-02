"""Fixed, manager-owned content for the one HotelApp property."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class HotelProfile(models.Model):
    """The one editable source of public hotel identity and fixed CMS blocks."""

    id = models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True)
    name = models.CharField("название гостиницы", max_length=160)
    tagline = models.CharField("короткое описание", max_length=240)
    about_title = models.CharField("заголовок блока «О гостинице»", max_length=200)
    about_text = models.TextField("текст блока «О гостинице»")
    address = models.CharField("адрес", max_length=255)
    phone = models.CharField("телефон", max_length=32)
    email = models.EmailField("email")
    check_in_time = models.TimeField("время заезда", default="14:00")
    check_out_time = models.TimeField("время выезда", default="12:00")
    footer_text = models.CharField("текст в footer", max_length=255)
    seo_title = models.CharField("SEO title", max_length=160)
    seo_description = models.CharField("SEO description", max_length=320)
    seo_keywords = models.CharField("SEO keywords", blank=True, max_length=255)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(pk=1),
                name="content_hotel_profile_is_singleton",
            )
        ]
        verbose_name = "профиль гостиницы"
        verbose_name_plural = "профиль гостиницы"

    def clean(self) -> None:
        super().clean()
        if self.pk != 1:
            raise ValidationError({"id": "В HotelApp может быть только один профиль гостиницы."})

    def __str__(self) -> str:
        return self.name


class HeroSlide(models.Model):
    """An ordered slide in the public landing-page hero."""

    profile = models.ForeignKey(
        HotelProfile,
        on_delete=models.CASCADE,
        related_name="hero_slides",
        verbose_name="профиль гостиницы",
    )
    eyebrow = models.CharField("надзаголовок", max_length=80)
    title = models.CharField("заголовок", max_length=200)
    body = models.TextField("текст", blank=True)
    image_url = models.URLField("URL изображения", blank=True)
    primary_cta_label = models.CharField("текст основной кнопки", blank=True, max_length=80)
    primary_cta_url = models.CharField("ссылка основной кнопки", blank=True, max_length=255)
    secondary_cta_label = models.CharField("текст дополнительной кнопки", blank=True, max_length=80)
    secondary_cta_url = models.CharField("ссылка дополнительной кнопки", blank=True, max_length=255)
    sort_order = models.PositiveSmallIntegerField("порядок", default=0)
    is_active = models.BooleanField("показывать", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "hero-слайд"
        verbose_name_plural = "hero-слайды"

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}
        for label_field, url_field in (
            ("primary_cta_label", "primary_cta_url"),
            ("secondary_cta_label", "secondary_cta_url"),
        ):
            if bool(getattr(self, label_field)) != bool(getattr(self, url_field)):
                errors[url_field] = "У кнопки должны быть заполнены и текст, и ссылка."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.title


class HotelFeature(models.Model):
    """An ordered fixed advantage card displayed on the public landing page."""

    profile = models.ForeignKey(
        HotelProfile,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name="профиль гостиницы",
    )
    icon = models.CharField(
        "иконка",
        help_text="Короткий символ или эмодзи для карточки преимущества.",
        max_length=16,
    )
    title = models.CharField("заголовок", max_length=120)
    description = models.TextField("описание")
    sort_order = models.PositiveSmallIntegerField("порядок", default=0)
    is_active = models.BooleanField("показывать", default=True)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "преимущество гостиницы"
        verbose_name_plural = "преимущества гостиницы"

    def __str__(self) -> str:
        return self.title
