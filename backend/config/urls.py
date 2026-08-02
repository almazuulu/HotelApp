"""Root URL configuration.

The public API contract is versioned below `/api/v1/`. Domain apps add endpoints
to this namespace in their own tickets.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(("config.api_urls", "api"), namespace="api-v1")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
