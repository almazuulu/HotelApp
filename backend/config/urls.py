"""Root URL configuration.

`/api/v1/`, the OpenAPI schema and Swagger UI are added by the backend scaffolding
and API contract issues. Only the admin and local media serving exist today.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

