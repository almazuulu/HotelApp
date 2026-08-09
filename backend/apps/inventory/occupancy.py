"""Availability search over physical rooms and existing booking occupancy."""

from __future__ import annotations

from collections.abc import Sequence

from django.db.models import Q
from django.utils import timezone

from apps.bookings.models import ACTIVE_BOOKING_STATUSES, Booking, BookingStatus
from apps.bookings.stay_policy import Stay

from .models import RoomType


class OccupancyLedger:
    """Own expiry cleanup and availability calculations for room categories."""

    def search(self, stay: Stay, adults: int, children: int) -> Sequence[RoomType]:
        """Return categories that fit the guests and still have a physical room."""

        now = timezone.now()
        self.expire_holds(now)
        candidates = RoomType.objects.filter(
            max_adults__gte=adults,
            max_children__gte=children,
        ).prefetch_related("rooms")

        available: list[RoomType] = []
        for room_type in candidates:
            room_count = len(room_type.rooms.all())
            occupied_count = Booking.objects.filter(
                room_type=room_type,
                check_in__lt=stay.check_out,
                check_out__gt=stay.check_in,
            ).filter(
                Q(status=BookingStatus.PAID)
                | Q(status__in=ACTIVE_BOOKING_STATUSES, expires_at__gt=now)
            ).count()
            if room_count > occupied_count:
                available.append(room_type)
        return available

    @staticmethod
    def expire_holds(now) -> int:
        """Release expired active holds before calculating current availability."""

        return Booking.objects.filter(
            status__in=ACTIVE_BOOKING_STATUSES,
            expires_at__lte=now,
        ).update(status=BookingStatus.EXPIRED, expires_at=None)


occupancy_ledger = OccupancyLedger()
