"""Read-only public serializers for the inventory catalog."""

from rest_framework import serializers

from .models import Amenity, ConfirmationMode, RoomType, RoomTypeImage


class AmenitySerializer(serializers.ModelSerializer[Amenity]):
    class Meta:
        model = Amenity
        fields = ("name", "slug")


class RoomTypeImageSerializer(serializers.ModelSerializer[RoomTypeImage]):
    class Meta:
        model = RoomTypeImage
        fields = ("image_url", "alt_text")


class RoomTypeSerializer(serializers.ModelSerializer[RoomType]):
    """The customer-safe catalog DTO; physical rooms and all IDs stay internal."""

    amenities = AmenitySerializer(many=True, read_only=True)
    images = RoomTypeImageSerializer(many=True, read_only=True)
    price_per_night = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=True,
        read_only=True,
    )
    area_sqm = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        coerce_to_string=True,
        read_only=True,
    )
    max_children = serializers.IntegerField(read_only=True)
    confirmation_mode = serializers.ChoiceField(
        choices=ConfirmationMode.choices,
        read_only=True,
    )

    class Meta:
        model = RoomType
        fields = (
            "name",
            "slug",
            "description",
            "price_per_night",
            "max_adults",
            "max_children",
            "area_sqm",
            "bed_count",
            "confirmation_mode",
            "amenities",
            "images",
        )


class RoomTypeFilterSerializer(serializers.Serializer[dict[str, object]]):
    """Validate the optional public catalog filters before querying the database."""

    adults = serializers.IntegerField(min_value=1, required=False)
    children = serializers.IntegerField(min_value=0, required=False)
    amenity = serializers.ListField(
        child=serializers.SlugField(),
        required=False,
    )
