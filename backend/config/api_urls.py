"""URLs owned by the version-one public API contract."""

from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config.api import api_root, csrf

app_name = "api"

urlpatterns = [
    path("", api_root, name="root"),
    path("csrf/", csrf, name="csrf"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api-v1:schema"), name="docs"),
]
