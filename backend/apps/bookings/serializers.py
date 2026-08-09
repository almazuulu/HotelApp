"""Public request and response serializers for booking quotes."""

from rest_framework import serializers


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
