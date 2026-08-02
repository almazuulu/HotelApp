"""Admin configuration for managers; customers remain non-staff by default."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Expose customer contact fields to managers without changing permissions."""

    fieldsets = DjangoUserAdmin.fieldsets + (("Контактные данные", {"fields": ("phone",)}),)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Контактные данные", {"fields": ("email", "first_name", "last_name", "phone")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "phone", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
