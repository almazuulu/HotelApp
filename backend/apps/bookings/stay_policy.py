"""Rules for a requested hotel stay window."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.utils import timezone

from config.errors import ApiErrorCode, DomainError

CHECK_IN_CUTOFF = time(hour=14)
MAX_STAY_NIGHTS = 30
BOOKING_HORIZON_DAYS = 365


@dataclass(frozen=True)
class Stay:
    """A validated half-open accommodation interval."""

    check_in: date
    check_out: date

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days


def validate_stay(check_in: date, check_out: date, now: datetime) -> Stay:
    """Validate the public stay-window policy and return its value object."""

    local_now = timezone.localtime(now)
    today = local_now.date()
    nights = (check_out - check_in).days

    is_today_after_cutoff = check_in == today and local_now.time() >= CHECK_IN_CUTOFF
    is_outside_horizon = check_in > today + timedelta(days=BOOKING_HORIZON_DAYS)
    if (
        check_in < today
        or is_today_after_cutoff
        or is_outside_horizon
        or not 1 <= nights <= MAX_STAY_NIGHTS
    ):
        raise DomainError(ApiErrorCode.STAY_WINDOW_INVALID)

    return Stay(check_in=check_in, check_out=check_out)
