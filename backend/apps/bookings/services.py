"""Lifecycle writes for bookings, kept separate from HTTP views."""

from __future__ import annotations

from datetime import datetime

from django.db import transaction

from apps.inventory.occupancy import release
from config.errors import ApiErrorCode, DomainError

from .models import ACTIVE_BOOKING_STATUSES, TERMINAL_BOOKING_STATUSES, Booking, BookingStatus


def expire_stale_holds(now: datetime) -> int:
    """Transition expired holds before any customer-visible booking response."""

    with transaction.atomic():
        stale_bookings = list(
            Booking.objects.select_for_update()
            .filter(status__in=ACTIVE_BOOKING_STATUSES, expires_at__lte=now)
            .select_related("room_type")
        )
        for booking in stale_bookings:
            release(booking)

        for booking in stale_bookings:
            booking.status = BookingStatus.EXPIRED
            booking.expires_at = None
            booking.save(update_fields=("status", "expires_at", "updated_at"))
    return len(stale_bookings)


def cancel_booking(booking: Booking, now: datetime) -> Booking:
    """Cancel an owned booking and release its assigned room through the ledger."""

    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(pk=booking.pk)
        if booking.status in TERMINAL_BOOKING_STATUSES:
            raise DomainError(ApiErrorCode.TRANSITION_NOT_ALLOWED)
        if booking.cancellable_until is not None and now >= booking.cancellable_until:
            raise DomainError(ApiErrorCode.CANCELLATION_WINDOW_PASSED)
        release(booking)
        booking.status = BookingStatus.CANCELLED
        booking.expires_at = None
        booking.save(update_fields=("status", "expires_at", "updated_at"))
    return booking
