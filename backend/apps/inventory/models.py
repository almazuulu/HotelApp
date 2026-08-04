"""Catalog models owned by the inventory module."""

from __future__ import annotations

from django.db import models
from django.db.models import Q


class Amenity(models.Model):
    """A guest-facing feature that can be attached to a room category."""

    name = models.CharField("название", max_length=120)
    slug = models.SlugField("slug", max_length=120, unique=True)

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "удобство"
        verbose_name_plural = "удобства"

    def __str__(self) -> str:
        return self.name


class ConfirmationMode(models.TextChoices):
    """How a newly created booking for a category is confirmed."""

    AUTOMATIC = "automatic", "автоматическое"
    MANUAL = "manual", "ручное"


class RoomType(models.Model):
    """The public category a customer chooses before a physical room is assigned."""

    name = models.CharField("название", max_length=160)
    slug = models.SlugField("slug", max_length=160, unique=True)
    description = models.TextField("описание")
    price_per_night = models.DecimalField("цена за ночь", max_digits=10, decimal_places=2)
    max_adults = models.PositiveSmallIntegerField("максимум взрослых")
    max_children = models.PositiveSmallIntegerField("максимум детей", default=0)
    area_sqm = models.DecimalField("площадь, м²", max_digits=6, decimal_places=2)
    bed_count = models.PositiveSmallIntegerField("количество кроватей")
    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name="room_types",
        verbose_name="удобства",
    )
    confirmation_mode = models.CharField(
        "режим подтверждения",
        choices=ConfirmationMode.choices,
        default=ConfirmationMode.AUTOMATIC,
        max_length=16,
    )

    class Meta:
        ordering = ("name", "pk")
        constraints = [
            models.CheckConstraint(
                condition=Q(price_per_night__gt=0),
                name="inventory_room_type_price_gt_zero",
            ),
            models.CheckConstraint(
                condition=Q(area_sqm__gt=0),
                name="inventory_room_type_area_gt_zero",
            ),
            models.CheckConstraint(
                condition=Q(max_adults__gte=1),
                name="inventory_room_type_adults_gte_one",
            ),
            models.CheckConstraint(
                condition=Q(max_children__gte=0),
                name="inventory_room_type_children_gte_zero",
            ),
            models.CheckConstraint(
                condition=Q(bed_count__gte=1),
                name="inventory_room_type_beds_gte_one",
            ),
        ]
        permissions = (
            (
                "manage_roomtype_commercial_fields",
                "Может управлять коммерческими полями категории номера",
            ),
        )
        verbose_name = "категория номера"
        verbose_name_plural = "категории номеров"

    def __str__(self) -> str:
        return self.name


class RoomTypeImage(models.Model):
    """An ordered, public image URL for a room category gallery."""

    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="категория номера",
    )
    image_url = models.URLField("URL изображения")
    alt_text = models.CharField("альтернативный текст", max_length=255)
    sort_order = models.PositiveSmallIntegerField("порядок", default=0)

    class Meta:
        ordering = ("sort_order", "pk")
        verbose_name = "изображение категории номера"
        verbose_name_plural = "изображения категорий номеров"

    def __str__(self) -> str:
        return self.alt_text


class Room(models.Model):
    """An internal physical room; its string number intentionally preserves leading zeroes."""

    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name="rooms",
        verbose_name="категория номера",
    )
    number = models.CharField("номер", max_length=32, unique=True)

    class Meta:
        ordering = ("number", "pk")
        verbose_name = "комната"
        verbose_name_plural = "комнаты"

    def __str__(self) -> str:
        return self.number
