"""Read-only public serializers for the fixed hotel CMS."""

from rest_framework import serializers

from .models import HeroSlide, HotelFeature, HotelProfile


class HeroSlideSerializer(serializers.ModelSerializer[HeroSlide]):
    class Meta:
        model = HeroSlide
        fields = (
            "eyebrow",
            "title",
            "body",
            "image_url",
            "primary_cta_label",
            "primary_cta_url",
            "secondary_cta_label",
            "secondary_cta_url",
        )


class HotelFeatureSerializer(serializers.ModelSerializer[HotelFeature]):
    class Meta:
        model = HotelFeature
        fields = ("icon", "title", "description")


class SiteContentSerializer(serializers.ModelSerializer[HotelProfile]):
    """The complete public CMS document; it intentionally has no write path."""

    hero_slides = HeroSlideSerializer(many=True, read_only=True)
    features = HotelFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = HotelProfile
        fields = (
            "name",
            "tagline",
            "about_title",
            "about_text",
            "address",
            "phone",
            "email",
            "check_in_time",
            "check_out_time",
            "footer_text",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "hero_slides",
            "features",
        )
