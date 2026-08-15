"""The inventory-owned occupancy ledger interface."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.postgres.fields.ranges import DateRange
from django.db import IntegrityError, connection, transaction
from django.db.models import Exists, OuterRef, QuerySet
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.stay_policy import Stay
from config.errors import ApiErrorCode, DomainError

from .models import MaintenanceBlock, Room, RoomOccupancy, RoomType

if TYPE_CHECKING:
    from django.db.models import Model


OCCUPANCY_EXCLUSION_CONSTRAINT = "inventory_room_occupancy_no_overlapping_stays"

class RoomUnavailable(DomainError):
    """Raised when no physical room can be allocated over a stay interval."""

    def __init__(self) -> None:
        super().__init__(ApiErrorCode.ROOM_UNAVAILABLE)


def _stay_range(stay: Stay) -> DateRange:
    return DateRange(stay.check_in, stay.check_out, bounds="[)")


def _delete_stale_booking_occupancies() -> None:
    RoomOccupancy.objects.filter(booking__expires_at__lte=timezone.now()).delete()


def _holder_field(holder: Booking | MaintenanceBlock) -> dict[str, Model]:
    if isinstance(holder, Booking):
        return {"booking": holder}
    if isinstance(holder, MaintenanceBlock):
        return {"maintenance_block": holder}
    raise TypeError("holder must be a Booking or MaintenanceBlock")


def _is_exclusion_constraint_violation(error: IntegrityError) -> bool:
    current: BaseException | None = error
    while current is not None:
        diagnostic = getattr(current, "diag", None)
        if getattr(diagnostic, "constraint_name", None) == OCCUPANCY_EXCLUSION_CONSTRAINT:
            return True
        current = current.__cause__
    return False


def search(stay: Stay, adults: int, children: int) -> QuerySet[RoomType]:
    """Return room categories with a free physical room for the whole stay."""

    stay_range = _stay_range(stay)
    with transaction.atomic():
        _delete_stale_booking_occupancies()

        occupied_rooms = RoomOccupancy.objects.filter(
            room_id=OuterRef("pk"),
            stay__overlap=stay_range,
        )
        available_rooms = Room.objects.filter(room_type_id=OuterRef("pk")).filter(
            ~Exists(occupied_rooms)
        )
        return (
            RoomType.objects.filter(max_adults__gte=adults)
            .filter(max_children__gte=children)
            .filter(Exists(available_rooms))
        )


def allocate(room_type: RoomType, stay: Stay, holder: Booking | MaintenanceBlock) -> None:
    """Allocate one physical room and persist its occupancy inside a transaction."""

    holder_field = _holder_field(holder)
    if holder.pk is None:
        raise ValueError("holder must be saved before allocation")
    if isinstance(holder, Booking) and holder.room_type_id != room_type.pk:
        raise ValueError("booking room type must match the allocation room type")

    stay_range = _stay_range(stay)
    with transaction.atomic():
        _delete_stale_booking_occupancies()

        candidate_rooms = Room.objects.select_for_update().filter(room_type=room_type)
        if isinstance(holder, MaintenanceBlock):
            candidate_rooms = candidate_rooms.filter(pk=holder.room_id)

        for room in candidate_rooms:
            if RoomOccupancy.objects.filter(room=room, stay__overlap=stay_range).exists():
                continue
            try:
                with transaction.atomic():
                    RoomOccupancy.objects.create(room=room, stay=stay_range, **holder_field)
            except IntegrityError as error:
                if _is_exclusion_constraint_violation(error):
                    raise RoomUnavailable from error
                raise
            return

    raise RoomUnavailable


def release(holder: Booking | MaintenanceBlock) -> None:
    """Idempotently remove the occupancy held by one booking or maintenance block."""

    if connection.vendor != "postgresql" or holder.pk is None:
        return
    RoomOccupancy.objects.filter(**_holder_field(holder)).delete()
