"""The single owner of allowed booking lifecycle transitions."""

from __future__ import annotations

from datetime import datetime

from django.db import transaction

from apps.inventory import occupancy
from config.errors import ApiErrorCode, DomainError

from .models import ACTIVE_BOOKING_STATUSES, TERMINAL_BOOKING_STATUSES, Booking, BookingStatus

ALLOWED_TRANSITIONS: dict[BookingStatus, frozenset[BookingStatus]] = {
    BookingStatus.PENDING_CONFIRMATION: frozenset(
        {
            BookingStatus.AWAITING_PAYMENT,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
            BookingStatus.EXPIRED,
        }
    ),
    BookingStatus.AWAITING_PAYMENT: frozenset(
        {
            BookingStatus.PAID,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
            BookingStatus.EXPIRED,
        }
    ),
    BookingStatus.PAID: frozenset(),
    BookingStatus.REJECTED: frozenset(),
    BookingStatus.CANCELLED: frozenset(),
    BookingStatus.EXPIRED: frozenset(),
}


def _ensure_transition_allowed(booking: Booking, target: BookingStatus) -> None:
    """Check one lifecycle edge against the central transition table."""

    if target not in ALLOWED_TRANSITIONS[BookingStatus(booking.status)]:
        raise DomainError(ApiErrorCode.TRANSITION_NOT_ALLOWED)


def _transition(booking: Booking, target: BookingStatus) -> Booking:
    """Apply one validated transition while the booking row is locked."""

    _ensure_transition_allowed(booking, target)
    if target in TERMINAL_BOOKING_STATUSES:
        occupancy.release(booking)
        booking.expires_at = None
    booking.status = target
    booking.save(update_fields=("status", "expires_at", "updated_at"))
    return booking


def expire_stale_holds(now: datetime) -> int:
    """Expire stale active holds and release their occupancy through the ledger."""

    with transaction.atomic():
        stale_bookings = list(
            Booking.objects.select_for_update().filter(
                status__in=ACTIVE_BOOKING_STATUSES,
                expires_at__lte=now,
            )
        )
        for booking in stale_bookings:
            _transition(booking, BookingStatus.EXPIRED)
    return len(stale_bookings)


def cancel_booking(booking: Booking, now: datetime) -> Booking:
    """Cancel an owned booking only when its lifecycle and deadline permit it."""

    with transaction.atomic():
        locked_booking = Booking.objects.select_for_update().get(pk=booking.pk)
        _ensure_transition_allowed(locked_booking, BookingStatus.CANCELLED)
        if locked_booking.cancellable_until is not None and now >= locked_booking.cancellable_until:
            raise DomainError(ApiErrorCode.CANCELLATION_WINDOW_PASSED)
        return _transition(locked_booking, BookingStatus.CANCELLED)
