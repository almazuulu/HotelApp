"""Internal booking model owned by the bookings module."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class BookingStatus(models.TextChoices):
    """The only booking states allowed by the lifecycle specification."""

    PENDING_CONFIRMATION = "pending_confirmation", "ожидает подтверждения"
    AWAITING_PAYMENT = "awaiting_payment", "ожидает оплаты"
    PAID = "paid", "оплачена"
    REJECTED = "rejected", "отклонена"
    CANCELLED = "cancelled", "отменена"
    EXPIRED = "expired", "истекла"


ACTIVE_BOOKING_STATUSES = (
    BookingStatus.PENDING_CONFIRMATION,
    BookingStatus.AWAITING_PAYMENT,
)

TERMINAL_BOOKING_STATUSES = (
    BookingStatus.REJECTED,
    BookingStatus.CANCELLED,
    BookingStatus.EXPIRED,
)

NON_EXPIRING_BOOKING_STATUSES = (
    BookingStatus.PAID,
    *TERMINAL_BOOKING_STATUSES,
)


class Booking(models.Model):
    """An internal booking foundation, before lifecycle, price, and API concerns exist."""

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="клиент",
    )
    room_type = models.ForeignKey(
        "inventory.RoomType",
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="категория номера",
    )
    check_in = models.DateField("заезд")
    check_out = models.DateField("выезд")
    adults = models.PositiveSmallIntegerField("взрослые")
    children = models.PositiveSmallIntegerField("дети")
    status = models.CharField("статус", choices=BookingStatus.choices, max_length=24)
    hold_expires_at = models.DateTimeField("срок удержания", null=True, blank=True)
    payment_due_at = models.DateTimeField("срок оплаты", null=True, blank=True)
    cancellable_until = models.DateTimeField("отмена доступна до", null=True, blank=True)
    expires_at = models.DateTimeField("истекает", null=True, blank=True)
    created_at = models.DateTimeField("создана", auto_now_add=True)
    updated_at = models.DateTimeField("обновлена", auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(check_in__lt=models.F("check_out")),
                name="bookings_booking_check_in_before_check_out",
            ),
            models.CheckConstraint(
                condition=Q(adults__gte=1),
                name="bookings_booking_adults_gte_one",
            ),
            models.CheckConstraint(
                condition=Q(children__gte=0),
                name="bookings_booking_children_gte_zero",
            ),
            models.CheckConstraint(
                condition=Q(status__in=BookingStatus.values),
                name="bookings_booking_status_allowed",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status__in=ACTIVE_BOOKING_STATUSES, expires_at__isnull=False)
                    | Q(status__in=NON_EXPIRING_BOOKING_STATUSES, expires_at__isnull=True)
                ),
                name="bookings_booking_expires_at_matches_status",
            ),
        ]
        verbose_name = "бронь"
        verbose_name_plural = "брони"

    def __str__(self) -> str:
        return str(self.reference)
