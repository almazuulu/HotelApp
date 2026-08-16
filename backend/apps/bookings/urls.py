"""Public URLs owned by the bookings module."""

from django.urls import path

from .views import booking_cancel, booking_detail, booking_list, quote

app_name = "bookings"

urlpatterns = [
    path("quotes/", quote, name="quote"),
    path("bookings/", booking_list, name="booking-list"),
    path("bookings/<uuid:reference>/", booking_detail, name="booking-detail"),
    path("bookings/<uuid:reference>/cancel/", booking_cancel, name="booking-cancel"),
]
