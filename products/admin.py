"""
Django admin configuration for the products application.

Registers Category, Tag, and Product models with the Django admin
interface, with customized display columns, search fields, and
filter options to facilitate efficient data population and management.

Usage:
    After creating a superuser (python manage.py createsuperuser),
    navigate to /admin/ to add, edit, and delete categories, tags,
    and products through the web interface.
"""

from django.contrib import admin

from .models import Category, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Category model.

    Features:
        - list_display: Shows category name in the list view.
        - search_fields: Enables searching categories by name.
    """

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Tag model.

    Features:
        - list_display: Shows tag name in the list view.
        - search_fields: Enables searching tags by name.
    """

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Product model.

    Features:
        - list_display: Shows key product fields at a glance in the list view.
        - list_filter: Adds sidebar filters for category and tags, allowing
          quick filtering when managing large product catalogs.
        - search_fields: Enables searching products by name, description, or SKU.
        - filter_horizontal: Replaces the default multi-select for tags with a
          more user-friendly dual-pane widget for adding/removing tags.
        - readonly_fields: Prevents editing of auto-managed timestamp fields.
    """

    list_display = ("name", "sku", "category", "price", "created_at")
    list_filter = ("category", "tags")
    search_fields = ("name", "description", "sku")
    filter_horizontal = ("tags",)  # User-friendly M2M widget
    readonly_fields = ("created_at", "updated_at")
