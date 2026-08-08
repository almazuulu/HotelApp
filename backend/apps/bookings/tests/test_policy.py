from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from apps.bookings.policy import (
    BUSINESS_TIME_ZONE,
    BookingDeadlines,
    StayWindowInvalid,
    deadlines,
    validate_stay,
)
from config.errors import ApiErrorCode


def test_same_day_check_in_is_allowed_until_135959_bishkek() -> None:
    now = datetime(2026, 9, 10, 13, 59, 59, tzinfo=BUSINESS_TIME_ZONE)

    validate_stay(date(2026, 9, 10), date(2026, 9, 11), now)


@pytest.mark.parametrize(
    "now",
    [
        datetime(2026, 9, 10, 14, 0, tzinfo=BUSINESS_TIME_ZONE),
        datetime(2026, 9, 10, 8, 0, tzinfo=UTC),
        datetime(2026, 9, 10, 16, 0, tzinfo=ZoneInfo("Asia/Kuala_Lumpur")),
    ],
)
def test_same_day_check_in_is_rejected_from_1400_bishkek(now: datetime) -> None:
    with pytest.raises(StayWindowInvalid) as error:
        validate_stay(date(2026, 9, 10), date(2026, 9, 11), now)

    assert error.value.code == ApiErrorCode.STAY_WINDOW_INVALID


@pytest.mark.parametrize(
    ("check_in", "check_out"),
    [
        (date(2026, 9, 9), date(2026, 9, 10)),
        (date(2026, 9, 11), date(2026, 9, 11)),
        (date(2026, 9, 11), date(2026, 10, 12)),
    ],
)
def test_invalid_past_or_night_count_stays_raise_a_domain_error(
    check_in: date, check_out: date
) -> None:
    with pytest.raises(StayWindowInvalid):
        validate_stay(check_in, check_out, datetime(2026, 9, 10, 12, tzinfo=BUSINESS_TIME_ZONE))


@pytest.mark.parametrize(
    ("check_in", "check_out"),
    [
        (date(2026, 9, 11), date(2026, 9, 12)),
        (date(2026, 9, 11), date(2026, 10, 11)),
    ],
)
def test_one_and_thirty_night_stays_are_valid(check_in: date, check_out: date) -> None:
    validate_stay(check_in, check_out, datetime(2026, 9, 10, 12, tzinfo=BUSINESS_TIME_ZONE))


@pytest.mark.parametrize(
    ("check_in", "should_raise"),
    [
        (date(2027, 9, 10), False),
        (date(2027, 9, 11), True),
    ],
)
def test_booking_horizon_is_inclusive_at_365_days(check_in: date, should_raise: bool) -> None:
    now = datetime(2026, 9, 10, 12, tzinfo=BUSINESS_TIME_ZONE)

    if should_raise:
        with pytest.raises(StayWindowInvalid):
            validate_stay(check_in, check_in + timedelta(days=1), now)
    else:
        validate_stay(check_in, check_in + timedelta(days=1), now)


@pytest.mark.parametrize("operation", [validate_stay, deadlines])
def test_naive_now_is_a_caller_error(operation) -> None:
    booking = SimpleNamespace(check_in=date(2026, 9, 11))

    with pytest.raises(ValueError, match="timezone-aware"):
        if operation is validate_stay:
            operation(date(2026, 9, 11), date(2026, 9, 12), datetime(2026, 9, 10, 12))
        else:
            operation(booking, datetime(2026, 9, 10, 12))


def test_deadlines_use_the_lifecycle_entry_time_in_bishkek() -> None:
    booking = SimpleNamespace(check_in=date(2026, 9, 5))

    result = deadlines(booking, datetime(2026, 9, 1, 12, tzinfo=UTC))

    assert result == BookingDeadlines(
        hold_expires_at=datetime(2026, 9, 2, 18, tzinfo=BUSINESS_TIME_ZONE),
        payment_due_at=datetime(2026, 9, 1, 18, 30, tzinfo=BUSINESS_TIME_ZONE),
        cancellable_until=datetime(2026, 9, 5, 0, tzinfo=BUSINESS_TIME_ZONE),
    )


def test_deadlines_are_cut_off_at_check_in_and_midnight() -> None:
    booking = SimpleNamespace(check_in=date(2026, 9, 10))
    now = datetime(2026, 9, 10, 13, 45, tzinfo=BUSINESS_TIME_ZONE)

    result = deadlines(booking, now)

    assert result.hold_expires_at == datetime(2026, 9, 10, 14, tzinfo=BUSINESS_TIME_ZONE)
    assert result.payment_due_at == datetime(2026, 9, 10, 14, tzinfo=BUSINESS_TIME_ZONE)
    assert result.cancellable_until == datetime(2026, 9, 10, 0, tzinfo=BUSINESS_TIME_ZONE)
