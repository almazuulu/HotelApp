"""Public URLs owned by the content module."""

from django.urls import path

from .views import site_content

app_name = "content"

urlpatterns = [path("", site_content, name="site-content")]
