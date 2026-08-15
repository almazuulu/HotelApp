"""Read-side selectors for customer-visible bookings."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from django.db.models import Q, QuerySet
from django.http import Http404

from .models import TERMINAL_BOOKING_STATUSES, Booking


def owned_bookings(customer_id: int) -> QuerySet[Booking]:
    """Return only bookings owned by one customer, with public category data."""

    return Booking.objects.filter(customer_id=customer_id).select_related("room_type")


def get_owned_booking(customer_id: int, reference: UUID) -> Booking:
    """Return one owned booking or hide its existence from other customers."""

    try:
        return owned_bookings(customer_id).get(reference=reference)
    except Booking.DoesNotExist as error:
        raise Http404 from error


def history_bookings(customer_id: int, today: date) -> QuerySet[Booking]:
    """Bookings belong to history after checkout or on a terminal transition."""

    return (
        owned_bookings(customer_id)
        .filter(Q(check_out__lte=today) | Q(status__in=TERMINAL_BOOKING_STATUSES))
        .order_by("-check_in", "-pk")
    )


def active_bookings(customer_id: int, today: date) -> QuerySet[Booking]:
    """Bookings not yet checked out and not terminal are currently active."""

    return (
        owned_bookings(customer_id)
        .exclude(Q(check_out__lte=today) | Q(status__in=TERMINAL_BOOKING_STATUSES))
        .order_by("check_in", "pk")
    )
