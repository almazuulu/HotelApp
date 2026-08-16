"""Public request and response serializers for booking quotes."""

from rest_framework import serializers

from .models import Booking


class QuoteRequestSerializer(serializers.Serializer[dict[str, object]]):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    room_type = serializers.SlugField()
    adults = serializers.IntegerField(min_value=1)
    children = serializers.IntegerField(min_value=0)


class QuoteSerializer(serializers.Serializer[dict[str, object]]):
    available = serializers.BooleanField()
    nights = serializers.IntegerField(min_value=1)
    price_per_night = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=True,
    )
    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=True,
    )


class BookingSerializer(serializers.ModelSerializer[Booking]):
    """Customer-safe booking DTO; a physical room is never part of this API."""

    room_type = serializers.SlugRelatedField(read_only=True, slug_field="slug")

    class Meta:
        model = Booking
        fields = (
            "reference",
            "room_type",
            "check_in",
            "check_out",
            "adults",
            "children",
            "status",
            "hold_expires_at",
            "payment_due_at",
            "cancellable_until",
        )


class BookingListSerializer(serializers.Serializer):
    active = BookingSerializer(many=True)
    history = BookingSerializer(many=True)
