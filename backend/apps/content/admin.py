"""Django admin for manager- and content-editor-owned fixed CMS data."""

from django.contrib import admin
from django.db import models

from .models import HeroSlide, HotelFeature, HotelProfile


class HeroSlideInline(admin.TabularInline):
    model = HeroSlide
    formfield_overrides = {models.URLField: {"assume_scheme": "https"}}
    extra = 0
    fields = (
        "eyebrow",
        "title",
        "image_url",
        "sort_order",
        "is_active",
    )
    show_change_link = True


class HotelFeatureInline(admin.TabularInline):
    model = HotelFeature
    extra = 0
    fields = ("icon", "title", "sort_order", "is_active")
    show_change_link = True


@admin.register(HotelProfile)
class HotelProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Гостиница", {"fields": ("name", "tagline")}),
        ("О гостинице", {"fields": ("about_title", "about_text")}),
        ("Контакты", {"fields": ("address", "phone", "email")}),
        ("Заезд и выезд", {"fields": ("check_in_time", "check_out_time")}),
        ("Footer", {"fields": ("footer_text",)}),
        ("SEO", {"fields": ("seo_title", "seo_description", "seo_keywords")}),
    )
    inlines = (HeroSlideInline, HotelFeatureInline)

    def has_add_permission(self, request) -> bool:
        return not HotelProfile.objects.exists() and super().has_add_permission(request)


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    formfield_overrides = {models.URLField: {"assume_scheme": "https"}}
    list_display = ("title", "profile", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "eyebrow")


@admin.register(HotelFeature)
class HotelFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "profile", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
