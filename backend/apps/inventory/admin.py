"""Django admin for the manager-owned inventory catalog."""

from django.contrib import admin
from django.db import models

from .models import Amenity, Room, RoomType, RoomTypeImage

COMMERCIAL_FIELDS = (
    "price_per_night",
    "max_adults",
    "max_children",
    "confirmation_mode",
)


class RoomTypeImageInline(admin.TabularInline):
    model = RoomTypeImage
    formfield_overrides = {models.URLField: {"assume_scheme": "https"}}
    extra = 0
    fields = ("image_url", "alt_text", "sort_order")


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    inlines = (RoomTypeImageInline,)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("amenities",)

    def has_commercial_fields_permission(self, request) -> bool:
        return request.user.has_perm("inventory.manage_roomtype_commercial_fields")

    def get_list_display(self, request):
        fields = ("name", "slug", "area_sqm", "bed_count")
        if self.has_commercial_fields_permission(request):
            return fields + COMMERCIAL_FIELDS
        return fields

    def get_fieldsets(self, request, obj=None):
        marketing_fields = ("name", "slug", "description", "area_sqm", "bed_count", "amenities")
        fieldsets = [("Категория", {"fields": marketing_fields})]
        if self.has_commercial_fields_permission(request):
            fieldsets.append(("Коммерческие условия", {"fields": COMMERCIAL_FIELDS}))
        return fieldsets

    def get_exclude(self, request, obj=None):
        if self.has_commercial_fields_permission(request):
            return super().get_exclude(request, obj)
        return (*COMMERCIAL_FIELDS, *(super().get_exclude(request, obj) or ()))

    def has_add_permission(self, request) -> bool:
        return self.has_commercial_fields_permission(request) and super().has_add_permission(
            request
        )

    def has_delete_permission(self, request, obj=None) -> bool:
        return self.has_commercial_fields_permission(request) and super().has_delete_permission(
            request, obj
        )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "room_type")
    list_filter = ("room_type",)
    search_fields = ("number", "room_type__name", "room_type__slug")
