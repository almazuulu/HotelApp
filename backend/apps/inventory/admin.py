"""Django admin for the manager-owned inventory catalog."""

from django import forms
from django.contrib import admin
from django.db import models, transaction

from .models import Amenity, MaintenanceBlock, Room, RoomType, RoomTypeImage
from .occupancy import Stay, allocate, release

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


class MaintenanceBlockAdminForm(forms.ModelForm):
    check_in = forms.DateField(label="Начало", required=False)
    check_out = forms.DateField(label="Окончание", required=False)

    class Meta:
        model = MaintenanceBlock
        fields = ("room", "reason")

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk is not None:
            return cleaned_data
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        if check_in is None or check_out is None:
            raise forms.ValidationError("Укажите даты начала и окончания.")
        try:
            self.stay = Stay(check_in=check_in, check_out=check_out)
        except ValueError:
            raise forms.ValidationError("Дата окончания должна быть позже даты начала.") from None
        return cleaned_data


@admin.register(MaintenanceBlock)
class MaintenanceBlockAdmin(admin.ModelAdmin):
    form = MaintenanceBlockAdminForm
    list_display = ("room", "reason", "created_by", "created_at")
    list_filter = ("room__room_type",)
    search_fields = ("room__number", "reason", "created_by__username")

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return ((None, {"fields": ("room", "reason", "check_in", "check_out")}),)
        return ((None, {"fields": ("room", "reason", "created_by", "created_at", "updated_at")}),)

    def get_readonly_fields(self, request, obj=None):
        fields = ("created_at", "updated_at")
        if obj is not None:
            return ("room", "created_by", *fields)
        return fields

    def save_model(self, request, obj, form, change) -> None:
        if change:
            super().save_model(request, obj, form, change)
            return

        obj.created_by = request.user
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            allocate(obj.room.room_type, form.stay, obj)

    def delete_model(self, request, obj) -> None:
        with transaction.atomic():
            release(obj)
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        with transaction.atomic():
            for maintenance_block in queryset:
                release(maintenance_block)
            queryset.delete()
