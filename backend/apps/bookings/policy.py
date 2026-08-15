"""Pure stay-window validation and booking deadline calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from django.utils import timezone

from config.errors import ApiErrorCode, DomainError

BUSINESS_TIME_ZONE = ZoneInfo("Asia/Bishkek")
CHECK_IN_TIME = time(hour=14)
MAX_STAY_NIGHTS = 30
MAX_BOOKING_HORIZON_DAYS = 365


class BookingWithCheckIn(Protocol):
    """The minimum booking data required to calculate absolute deadlines."""

    check_in: date


@dataclass(frozen=True)
class BookingDeadlines:
    """The named lifecycle deadlines calculated in the business timezone."""

    hold_expires_at: datetime
    payment_due_at: datetime
    cancellable_until: datetime


class StayWindowInvalid(DomainError):
    """Raised when a stay does not fit the hotel booking window."""

    def __init__(self) -> None:
        super().__init__(ApiErrorCode.STAY_WINDOW_INVALID)


def _in_business_timezone(now: datetime) -> datetime:
    if timezone.is_naive(now):
        raise ValueError("now must be timezone-aware")
    return now.astimezone(BUSINESS_TIME_ZONE)


def validate_stay(check_in: date, check_out: date, now: datetime) -> None:
    """Validate the fixed MVP stay window without reading the database or a clock."""

    business_now = _in_business_timezone(now)
    nights = (check_out - check_in).days

    if (
        check_in < business_now.date()
        or not 1 <= nights <= MAX_STAY_NIGHTS
        or check_in > business_now.date() + timedelta(days=MAX_BOOKING_HORIZON_DAYS)
        or (check_in == business_now.date() and business_now.time() >= CHECK_IN_TIME)
    ):
        raise StayWindowInvalid


def deadlines(booking: BookingWithCheckIn, now: datetime) -> BookingDeadlines:
    """Calculate lifecycle deadlines from the supplied lifecycle-entry instant."""

    business_now = _in_business_timezone(now)
    check_in_at = datetime.combine(booking.check_in, CHECK_IN_TIME, tzinfo=BUSINESS_TIME_ZONE)

    return BookingDeadlines(
        hold_expires_at=min(business_now + timedelta(hours=24), check_in_at),
        payment_due_at=min(business_now + timedelta(minutes=30), check_in_at),
        cancellable_until=datetime.combine(booking.check_in, time.min, tzinfo=BUSINESS_TIME_ZONE),
    )
