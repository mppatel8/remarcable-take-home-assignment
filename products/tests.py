"""
Tests for the products application.

This module provides comprehensive test coverage for:
    - Model creation and string representations
    - Model relationships (ForeignKey and ManyToMany)
    - Database constraints (unique fields, PROTECT on delete)
    - The product_list view: search, filter, combined queries, and pagination

Test Strategy:
    - Each test method tests one specific behavior (single responsibility).
    - setUp() creates shared test data to avoid repetition.
    - Tests use Django's TestCase which wraps each test in a transaction
      and rolls back after completion, ensuring test isolation.
"""

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Category, Product, Tag


class CategoryModelTests(TestCase):
    """Tests for the Category model."""

    def test_create_category(self):
        """A category can be created with a name."""
        category = Category.objects.create(name="Test Category")
        self.assertEqual(category.name, "Test Category")

    def test_str_representation(self):
        """The string representation of a category is its name."""
        category = Category.objects.create(name="Plumbing")
        self.assertEqual(str(category), "Plumbing")

    def test_unique_name_constraint(self):
        """Creating two categories with the same name raises IntegrityError."""
        Category.objects.create(name="Unique Name")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Unique Name")

    def test_default_ordering(self):
        """Categories are ordered alphabetically by name by default."""
        Category.objects.create(name="Zeta")
        Category.objects.create(name="Alpha")
        Category.objects.create(name="Mu")
        names = list(Category.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha", "Mu", "Zeta"])


class TagModelTests(TestCase):
    """Tests for the Tag model."""

    def test_create_tag(self):
        """A tag can be created with a name."""
        tag = Tag.objects.create(name="Heavy-Duty")
        self.assertEqual(tag.name, "Heavy-Duty")

    def test_str_representation(self):
        """The string representation of a tag is its name."""
        tag = Tag.objects.create(name="Industrial")
        self.assertEqual(str(tag), "Industrial")

    def test_unique_name_constraint(self):
        """Creating two tags with the same name raises IntegrityError."""
        Tag.objects.create(name="Premium")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Premium")


class ProductModelTests(TestCase):
    """Tests for the Product model and its relationships."""

    def setUp(self):
        """Set up test data: one category, two tags, one product."""
        self.category = Category.objects.create(name="Building Materials")
        self.tag1 = Tag.objects.create(name="Industrial")
        self.tag2 = Tag.objects.create(name="Eco-Friendly")
        self.product = Product.objects.create(
            name="Portland Cement",
            description="Type I/II Portland cement for general construction.",
            price=13.50,
            sku="BLD-CEM-001",
            category=self.category,
        )
        self.product.tags.set([self.tag1, self.tag2])

    def test_create_product(self):
        """A product can be created with all required fields."""
        self.assertEqual(self.product.name, "Portland Cement")
        self.assertEqual(float(self.product.price), 13.50)

    def test_str_representation(self):
        """The string representation includes name and SKU."""
        self.assertEqual(str(self.product), "Portland Cement (BLD-CEM-001)")

    def test_category_relationship(self):
        """A product's category is accessible via the ForeignKey."""
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.category.name, "Building Materials")

    def test_reverse_category_relationship(self):
        """A category can access its products via the related_name."""
        self.assertIn(self.product, self.category.products.all())

    def test_tags_relationship(self):
        """A product can have multiple tags via ManyToMany."""
        self.assertEqual(self.product.tags.count(), 2)
        tag_names = set(self.product.tags.values_list("name", flat=True))
        self.assertEqual(tag_names, {"Industrial", "Eco-Friendly"})

    def test_reverse_tag_relationship(self):
        """A tag can access its products via the related_name."""
        self.assertIn(self.product, self.tag1.products.all())

    def test_product_without_tags(self):
        """A product can exist without any tags (blank=True)."""
        product = Product.objects.create(
            name="No Tags Product",
            description="A product with no tags.",
            price=5.00,
            sku="TEST-NOTAG",
            category=self.category,
        )
        self.assertEqual(product.tags.count(), 0)

    def test_unique_sku_constraint(self):
        """Creating two products with the same SKU raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name="Duplicate SKU",
                description="This should fail.",
                price=1.00,
                sku="BLD-CEM-001",  # Same SKU as setUp product
                category=self.category,
            )

    def test_category_protect_on_delete(self):
        """
        Deleting a category that has products raises ProtectedError.

        This tests the on_delete=PROTECT behavior which prevents
        accidental data loss from cascading deletes.
        """
        with self.assertRaises(ProtectedError):
            self.category.delete()


class ProductListViewTests(TestCase):
    """
    Tests for the product_list view.

    Tests cover search, filtering, combined queries, and pagination
    to ensure the view correctly handles all user interactions.
    """

    def setUp(self):
        """
        Set up test data for view tests.

        Creates:
            - 2 categories: Plumbing, Electrical
            - 3 tags: Industrial, Residential, Premium
            - 3 products with varying categories and tags
        """
        self.client = Client()
        self.url = reverse("products:product_list")

        # Categories
        self.plumbing = Category.objects.create(name="Plumbing")
        self.electrical = Category.objects.create(name="Electrical")

        # Tags
        self.industrial = Tag.objects.create(name="Industrial")
        self.residential = Tag.objects.create(name="Residential")
        self.premium = Tag.objects.create(name="Premium")

        # Product 1: Plumbing + Industrial + Residential
        self.pipe = Product.objects.create(
            name="Copper Pipe",
            description="High-quality copper pipe for residential plumbing.",
            price=12.99,
            sku="PLM-001",
            category=self.plumbing,
        )
        self.pipe.tags.set([self.industrial, self.residential])

        # Product 2: Electrical + Industrial + Premium
        self.panel = Product.objects.create(
            name="LED Panel",
            description="Energy-efficient LED panel for commercial use.",
            price=54.99,
            sku="ELC-001",
            category=self.electrical,
        )
        self.panel.tags.set([self.industrial, self.premium])

        # Product 3: Plumbing + Residential (no Industrial tag)
        self.valve = Product.objects.create(
            name="PVC Valve",
            description="Budget PVC valve for basic water control.",
            price=3.99,
            sku="PLM-002",
            category=self.plumbing,
        )
        self.valve.tags.set([self.residential])

    def test_view_loads_successfully(self):
        """The product list page loads with HTTP 200."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_all_products_displayed_by_default(self):
        """With no filters, all products are displayed."""
        response = self.client.get(self.url)
        self.assertEqual(response.context["total_results"], 3)

    def test_search_by_description(self):
        """Searching by description returns matching products (case-insensitive)."""
        response = self.client.get(self.url, {"search": "copper"})
        products = response.context["page_obj"].object_list
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Copper Pipe")

    def test_search_case_insensitive(self):
        """Description search is case-insensitive."""
        response = self.client.get(self.url, {"search": "COPPER"})
        products = response.context["page_obj"].object_list
        self.assertEqual(len(products), 1)

    def test_search_partial_match(self):
        """Description search matches partial text."""
        response = self.client.get(self.url, {"search": "plumbing"})
        products = response.context["page_obj"].object_list
        # "Copper Pipe" description contains "plumbing"
        self.assertEqual(len(products), 1)

    def test_search_no_results(self):
        """Searching for non-existent text returns no results."""
        response = self.client.get(self.url, {"search": "nonexistent"})
        self.assertEqual(response.context["total_results"], 0)

    def test_filter_by_category(self):
        """Filtering by category returns only products in that category."""
        response = self.client.get(self.url, {"category": self.plumbing.id})
        products = response.context["page_obj"].object_list
        self.assertEqual(len(products), 2)
        # Verify all results belong to the Plumbing category
        for product in products:
            self.assertEqual(product.category, self.plumbing)

    def test_filter_by_single_tag(self):
        """Filtering by a single tag returns products with that tag."""
        response = self.client.get(self.url, {"tags": [self.premium.id]})
        products = response.context["page_obj"].object_list
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "LED Panel")

    def test_filter_by_multiple_tags(self):
        """
        Filtering by multiple tags uses OR logic.

        A product with ANY of the selected tags should be returned.
        """
        response = self.client.get(
            self.url, {"tags": [self.premium.id, self.residential.id]}
        )
        products = response.context["page_obj"].object_list
        # Premium: LED Panel, Residential: Copper Pipe + PVC Valve → 3 products
        self.assertEqual(len(products), 3)

    def test_no_duplicate_results_with_multiple_tags(self):
        """
        Products matching multiple selected tags appear only once.

        The view should use distinct() to prevent duplicates from
        the M2M join when a product has multiple matching tags.
        """
        # Copper Pipe has both Industrial and Residential tags
        response = self.client.get(
            self.url, {"tags": [self.industrial.id, self.residential.id]}
        )
        products = response.context["page_obj"].object_list
        # All 3 products match (pipe has both, panel has industrial, valve has residential)
        self.assertEqual(len(products), 3)
        # Verify no duplicates by checking unique SKUs
        skus = [p.sku for p in products]
        self.assertEqual(len(skus), len(set(skus)))

    def test_combined_search_and_category_filter(self):
        """Search and category filter can be combined (AND logic)."""
        response = self.client.get(
            self.url,
            {"search": "copper", "category": self.plumbing.id},
        )
        products = response.context["page_obj"].object_list
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Copper Pipe")

    def test_combined_search_and_tag_filter(self):
        """Search and tag filter can be combined (AND logic)."""
        response = self.client.get(
            self.url,
            {"search": "energy", "tags": [self.premium.id]},
        )
        products = response.context["page_obj"].object_list
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "LED Panel")

    def test_combined_category_and_tag_filter(self):
        """Category and tag filters can be combined (AND logic)."""
        response = self.client.get(
            self.url,
            {"category": self.plumbing.id, "tags": [self.industrial.id]},
        )
        products = response.context["page_obj"].object_list
        # Only Copper Pipe is in Plumbing AND has the Industrial tag
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Copper Pipe")

    def test_combined_all_filters(self):
        """Search, category, and tag filters all work together."""
        response = self.client.get(
            self.url,
            {
                "search": "copper",
                "category": self.plumbing.id,
                "tags": [self.residential.id],
            },
        )
        products = response.context["page_obj"].object_list
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Copper Pipe")

    def test_combined_filters_no_match(self):
        """Combined filters that contradict each other return no results."""
        # Search for "copper" but filter by Electrical category — no match
        response = self.client.get(
            self.url,
            {"search": "copper", "category": self.electrical.id},
        )
        self.assertEqual(response.context["total_results"], 0)

    def test_filter_values_preserved_in_context(self):
        """
        The current filter values are passed back to the template context
        so the form can retain the user's selections after submission.
        """
        response = self.client.get(
            self.url,
            {
                "search": "test query",
                "category": str(self.plumbing.id),
                "tags": [str(self.industrial.id)],
            },
        )
        self.assertEqual(response.context["search_query"], "test query")
        self.assertEqual(response.context["selected_category"], str(self.plumbing.id))
        self.assertIn(str(self.industrial.id), response.context["selected_tags"])

    def test_categories_in_context(self):
        """All categories are available in the template context for the dropdown."""
        response = self.client.get(self.url)
        self.assertEqual(response.context["categories"].count(), 2)

    def test_tags_in_context(self):
        """All tags are available in the template context for the checkboxes."""
        response = self.client.get(self.url)
        self.assertEqual(response.context["tags"].count(), 3)

    def test_correct_template_used(self):
        """The view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product_list.html")

    def test_invalid_category_id_handled_gracefully(self):
        """Non-numeric category parameter does not raise 500 error."""
        response = self.client.get(self.url, {"category": "invalid_abc"})
        self.assertEqual(response.status_code, 200)

    def test_invalid_tag_id_handled_gracefully(self):
        """Non-numeric tag parameters do not raise 500 error."""
        response = self.client.get(self.url, {"tags": ["invalid_xyz"]})
        self.assertEqual(response.status_code, 200)

    def test_pagination_multiple_pages(self):
        """Products are paginated with 10 items per page."""
        # Create 12 more products to exceed page size of 10 (3 existing + 12 = 15)
        for i in range(12):
            Product.objects.create(
                name=f"Extra Product {i}",
                description=f"Description for extra product {i}",
                price=10.00 + i,
                sku=f"PAG-EXT-{i:03d}",
                category=self.plumbing,
            )
        response_p1 = self.client.get(self.url)
        self.assertEqual(response_p1.status_code, 200)
        self.assertEqual(len(response_p1.context["page_obj"]), 10)
        self.assertTrue(response_p1.context["page_obj"].has_next())

        response_p2 = self.client.get(self.url, {"page": 2})
        self.assertEqual(response_p2.status_code, 200)
        self.assertEqual(len(response_p2.context["page_obj"]), 5)
        self.assertFalse(response_p2.context["page_obj"].has_next())

    def test_pagination_invalid_page_handling(self):
        """Paginator handles non-integer or out-of-range page numbers gracefully."""
        # Out-of-range page delivers the last page
        response_out = self.client.get(self.url, {"page": 999})
        self.assertEqual(response_out.status_code, 200)
        # Non-integer page delivers the first page
        response_nan = self.client.get(self.url, {"page": "not_a_number"})
        self.assertEqual(response_nan.status_code, 200)

    def test_root_url_redirects_to_products(self):
        """Root URL '/' redirects to '/products/'."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/products/")
