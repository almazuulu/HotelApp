"""URLs owned by the version-one public API contract."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config.api import api_root, csrf

app_name = "api"

urlpatterns = [
    path("", api_root, name="root"),
    path("csrf/", csrf, name="csrf"),
    path("auth/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("", include(("apps.bookings.urls", "bookings"), namespace="bookings")),
    path("site/", include(("apps.content.urls", "content"), namespace="content")),
    path(
        "room-types/",
        include(("apps.inventory.urls", "inventory"), namespace="inventory"),
    ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api-v1:schema"), name="docs"),
]
