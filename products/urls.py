"""
URL configuration for the products application.

Defines URL patterns for product-related views. Uses the 'products'
namespace to avoid URL name collisions with other apps.

Usage in templates:
    {% url 'products:product_list' %}
"""

from django.urls import path

from . import views

# App namespace for URL reversing — allows {% url 'products:product_list' %}
# and prevents name collisions if other apps define a 'product_list' URL.
app_name = "products"

urlpatterns = [
    # Main product listing page with search and filter functionality
    path("", views.product_list, name="product_list"),
]
