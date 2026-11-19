"""
Root URL configuration for the project.

Routes:
    /admin/     → Django admin interface (for data population)
    /products/  → Product catalog with search and filter functionality
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin — used for populating categories, tags, and products
    path("admin/", admin.site.urls),
    # Product catalog — search and filter interface
    path("products/", include("products.urls")),
]
