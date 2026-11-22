"""
Views for the products application.

This module contains the product_list view which provides the core
search and filter functionality required by the assignment:
    - Search products by description (case-insensitive partial match)
    - Filter products by category (single-select dropdown)
    - Filter products by tags (multi-select checkboxes, OR logic)
    - Combine any/all of the above filters (AND logic between filter types)

Query Optimization Strategy:
    - select_related('category'): Performs a SQL JOIN to fetch each product's
      category in the same query, preventing N+1 queries when displaying
      category names in the template.
    - prefetch_related('tags'): Executes a single additional query to fetch
      all tags for the displayed products, rather than one query per product.
    - distinct(): Required when filtering by tags via M2M join, as a product
      matching multiple selected tags would otherwise appear multiple times.
"""

from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Category, Product, Tag


def product_list(request):
    """
    Display a searchable, filterable list of products with pagination.

    This view handles all search and filter logic through GET parameters,
    allowing filters to be combined freely. The filtering strategy uses
    progressive queryset chaining — each filter narrows the results further
    (AND logic between filter types).

    GET Parameters:
        search (str): Text to search within product descriptions.
            Uses icontains for case-insensitive partial matching.
        category (str): Category ID to filter by (exact match on FK).
        tags (list[str]): One or more Tag IDs to filter by.
            Uses OR logic within tags (product must have at least one).
        page (str): Page number for pagination (default: 1).

    Example URL:
        /products/?search=copper&category=1&tags=3&tags=7&page=2

    Query Flow:
        1. Start with all products (with optimized related data fetching)
        2. If search term → filter(description__icontains=search)
        3. If category → filter(category_id=category_id)
        4. If tags → filter(tags__id__in=tag_ids)
        5. Apply distinct() to eliminate M2M join duplicates
        6. Paginate results (10 per page)

    Context Variables:
        page_obj: Paginated page of Product objects.
        categories: All Category objects (for the filter dropdown).
        tags: All Tag objects (for the filter checkboxes).
        search_query: Current search text (to preserve form state).
        selected_category: Currently selected category ID string.
        selected_tags: List of currently selected tag ID strings.
        total_results: Total count of matching products.
    """
    # --- Extract filter parameters from the GET request ---
    search_query = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "")
    # getlist() retrieves multiple values for the same parameter name
    # This handles URLs like ?tags=1&tags=3&tags=7
    selected_tag_ids = request.GET.getlist("tags")

    # --- Build the queryset with progressive filtering ---

    # Start with all products, using select_related and prefetch_related
    # to optimize database queries and prevent N+1 query problems:
    #   - select_related('category') → SQL JOIN, single query for FK
    #   - prefetch_related('tags') → one additional query for all M2M tags
    queryset = Product.objects.select_related("category").prefetch_related("tags")

    # Apply description search filter (case-insensitive partial match)
    # icontains translates to SQL: WHERE description LIKE '%search%' (case-insensitive)
    if search_query:
        queryset = queryset.filter(description__icontains=search_query)

    # Apply category filter (exact match on the foreign key ID)
    # Validate category_id is numeric to prevent unhandled ValueError on malformed inputs
    if category_id and category_id.isdigit():
        queryset = queryset.filter(category_id=int(category_id))

    # Apply tag filter with OR logic: product must have AT LEAST ONE
    # of the selected tags. The __in lookup generates a SQL IN clause:
    #   WHERE tag_id IN (3, 7, 10)
    # Filter only valid numeric IDs to prevent unhandled ValueError
    valid_tag_ids = [t for t in selected_tag_ids if t.isdigit()]
    if valid_tag_ids:
        queryset = queryset.filter(tags__id__in=valid_tag_ids)

    # Remove duplicate rows that result from the M2M JOIN.
    # Without distinct(), a product matching 2 selected tags would appear twice.
    queryset = queryset.distinct()

    # --- Pagination: 10 products per page ---
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --- Fetch all categories and tags for the filter form ---
    # These queries are lightweight (small tables) and needed for form rendering
    all_categories = Category.objects.all()
    all_tags = Tag.objects.all()

    # --- Build template context ---
    # We pass back the current filter values so the template can:
    #   1. Pre-fill the search box with the current search term
    #   2. Mark the selected category in the dropdown
    #   3. Check the boxes for the currently selected tags
    context = {
        "page_obj": page_obj,
        "categories": all_categories,
        "tags": all_tags,
        "search_query": search_query,
        "selected_category": category_id,
        "selected_tags": selected_tag_ids,
        "total_results": paginator.count,
    }

    return render(request, "products/product_list.html", context)
