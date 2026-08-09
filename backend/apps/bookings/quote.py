"""Authoritative price quotes that never create inventory holds."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from apps.inventory.models import RoomType
from apps.inventory.occupancy import OccupancyLedger

from .stay_policy import Stay


@dataclass(frozen=True)
class Quote:
    available: bool
    nights: int
    price_per_night: Decimal
    total: Decimal


def calculate_quote(
    *,
    stay: Stay,
    room_type: RoomType,
    adults: int,
    children: int,
    ledger: OccupancyLedger,
) -> Quote:
    """Calculate the current quote without creating a booking or hold."""

    available_room_type_ids = {candidate.pk for candidate in ledger.search(stay, adults, children)}
    price_per_night = room_type.price_per_night
    return Quote(
        available=room_type.pk in available_room_type_ids,
        nights=stay.nights,
        price_per_night=price_per_night,
        total=price_per_night * stay.nights,
    )
