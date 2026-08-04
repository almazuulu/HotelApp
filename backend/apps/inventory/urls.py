"""Public URLs owned by the inventory module."""

from django.urls import path

from .views import room_type_detail, room_type_list

app_name = "inventory"

urlpatterns = [
    path("", room_type_list, name="room-type-list"),
    path("<slug:slug>/", room_type_detail, name="room-type-detail"),
]
