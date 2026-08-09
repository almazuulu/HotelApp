"""Public URLs owned by the bookings module."""

from django.urls import path

from .views import quote

app_name = "bookings"

urlpatterns = [path("", quote, name="quote")]
