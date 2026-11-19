"""
Models for the products application.

This module defines three core models that represent a product catalog:
    - Category: Groups products into logical categories (one-to-many with Product).
    - Tag: Flexible labels for cross-cutting concerns (many-to-many with Product).
    - Product: The central model representing items in the catalog.

Relationship Diagram:
    Category ──< Product >──< Tag
      (1:N via FK)    (M:N via junction table)

Design Decisions:
    - Category uses ForeignKey (one-to-many) because each product belongs to
      exactly one primary category, enforcing a strict hierarchy.
    - Tag uses ManyToManyField because tags are non-exclusive labels that can
      be freely combined across products (e.g., a product can be both
      "Heavy-Duty" and "Energy-Efficient").
    - on_delete=PROTECT on the Category FK prevents accidental data loss by
      blocking deletion of categories that still contain products.
"""

from django.db import models


class Category(models.Model):
    """
    Represents a product category for top-level organization.

    Each product belongs to exactly one category, establishing a
    one-to-many (ForeignKey) relationship from Product to Category.

    Examples: Plumbing Supplies, Electrical Equipment, Building Materials.

    Attributes:
        name (str): Unique display name for the category (max 100 chars).
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The display name for this category (must be unique).",
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]  # Alphabetical ordering by default

    def __str__(self):
        """Return the category name for admin and shell display."""
        return self.name


class Tag(models.Model):
    """
    Represents a descriptive tag for flexible product labeling.

    Tags have a many-to-many relationship with products, enabling
    multi-dimensional filtering beyond the primary category.

    Examples: Industrial, Residential, Heavy-Duty, Eco-Friendly.

    Attributes:
        name (str): Unique display name for the tag (max 50 chars).
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="The display name for this tag (must be unique).",
    )

    class Meta:
        ordering = ["name"]  # Alphabetical ordering by default

    def __str__(self):
        """Return the tag name for admin and shell display."""
        return self.name


class Product(models.Model):
    """
    Represents a product in the catalog.

    This is the central model with two key relationships:
        - category (ForeignKey → Category): Each product belongs to one category.
          Uses PROTECT to prevent deletion of categories that still have products.
        - tags (ManyToManyField → Tag): Products can have zero or more tags for
          flexible, multi-dimensional filtering.

    The 'related_name' attribute on each relationship enables reverse lookups:
        - category.products.all()  → all products in a given category
        - tag.products.all()       → all products with a specific tag

    Attributes:
        name (str): Display name of the product.
        description (str): Detailed description; this is the searchable field.
        price (Decimal): Product price in USD (up to 99,999,999.99).
        sku (str): Stock Keeping Unit — unique inventory identifier.
        category (FK): The single category this product belongs to.
        tags (M2M): Zero or more tags for additional classification.
        created_at (datetime): Auto-set when the product is first created.
        updated_at (datetime): Auto-set every time the product is saved.
    """

    name = models.CharField(
        max_length=200,
        help_text="The display name of the product.",
    )
    description = models.TextField(
        help_text="Detailed product description. This field is searchable by users.",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price in USD.",
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        help_text="Stock Keeping Unit — unique identifier for inventory tracking.",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # Prevent accidental category deletion
        related_name="products",   # Enables: category.products.all()
        help_text="The category this product belongs to.",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="products",  # Enables: tag.products.all()
        blank=True,               # Products are allowed to have no tags
        help_text="Tags for flexible filtering and categorization.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]  # Default alphabetical ordering
        indexes = [
            # Database index on category_id for faster FK-based filtering.
            # Django auto-creates an index for ForeignKey fields in most backends,
            # but being explicit documents our intent and ensures portability.
            models.Index(fields=["category"], name="idx_product_category"),
            # Index on name to speed up default ordering
            models.Index(fields=["name"], name="idx_product_name"),
        ]

    def __str__(self):
        """Return product name with SKU for easy identification."""
        return f"{self.name} ({self.sku})"
