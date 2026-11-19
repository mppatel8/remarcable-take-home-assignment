# Remarcable Take-Home Assignment — Product Catalog

A Django application that models products, categories, and tags with search and filter functionality.

## Features

- **Product Catalog** with categories (one-to-many) and tags (many-to-many)
- **Search** products by description (case-insensitive partial matching)
- **Filter** products by category (dropdown) and tags (multi-select checkboxes)
- **Combined Filters** — search, category, and tag filters work together (AND logic between filter types, OR logic within tags)
- **Pagination** — results are paginated (10 per page) with filter-preserving navigation
- **Admin Interface** — fully configured for easy data management
- **Optimized Queries** — uses `select_related` and `prefetch_related` to prevent N+1 query problems
- **Comprehensive Tests** — 35 tests covering models, relationships, constraints, and view logic

## Tech Stack

| Component | Version |
|-----------|---------|
| Python    | 3.12    |
| Django    | 6.1.3   |
| Database  | SQLite  |

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd remarcable_take_home_assignment
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Seed the Database (Option A — Quick Setup)

A management command is provided to populate the database with sample construction supply data (6 categories, 12 tags, 24 products):

```bash
python manage.py seed_data
```

### 5. Populate via Admin (Option B — Manual Entry)

Create a superuser and add data through the Django admin interface:

```bash
python manage.py createsuperuser
python manage.py runserver
# Navigate to http://127.0.0.1:8000/admin/
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Then open: **http://127.0.0.1:8000/products/**

### 7. Run Tests

```bash
python manage.py test products -v 2
```

## Project Structure

```
remarcable_take_home_assignment/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
├── config/                            # Project configuration
│   ├── settings.py                    # Django settings
│   ├── urls.py                        # Root URL routing
│   ├── wsgi.py                        # WSGI entry point
│   └── asgi.py                        # ASGI entry point
└── products/                          # Main application
    ├── models.py                      # Category, Tag, Product models
    ├── views.py                       # product_list view with search/filter
    ├── urls.py                        # App URL routing
    ├── admin.py                       # Admin interface configuration
    ├── tests.py                       # 35 unit tests
    ├── templates/
    │   └── products/
    │       └── product_list.html      # Search & filter UI
    └── management/
        └── commands/
            └── seed_data.py           # Database seeding command
```

## Data Model

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Category   │       │   Product    │       │     Tag      │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)      │    ┌──│ id (PK)      │
│ name (unique)│  │    │ name         │    │  │ name (unique)│
└──────────────┘  │    │ description  │    │  └──────────────┘
                  │    │ price        │    │
                  └───>│ sku (unique) │    │
                  FK   │ category (FK)│<───┘
                (1:N)  │ tags (M2M)   │  M2M
                       │ created_at   │ (via junction table)
                       │ updated_at   │
                       └──────────────┘
```

**Relationships:**
- **Category → Product**: One-to-Many (ForeignKey with `on_delete=PROTECT`)
- **Product ↔ Tag**: Many-to-Many (Django auto-creates the junction table)

## Query Strategy

The `product_list` view builds queries progressively:

1. **Base**: `Product.objects.select_related("category").prefetch_related("tags")`
2. **Search**: `.filter(description__icontains=search_term)` — case-insensitive partial match
3. **Category**: `.filter(category_id=category_id)` — exact FK match
4. **Tags**: `.filter(tags__id__in=tag_ids)` — OR within selected tags
5. **Dedup**: `.distinct()` — removes M2M join duplicates

Filters are combined with **AND logic** between types (search AND category AND tags), while multiple tags use **OR logic** within (product has tag A OR tag B).

## Design Decisions & Assumptions

- **`on_delete=PROTECT`** on the Category FK prevents accidental data loss. Deleting a category that still has products will raise a `ProtectedError` rather than cascade-deleting products.
- **Function-based view** was chosen over a class-based view to make the query logic explicit and easy to follow, directly demonstrating Django queryset proficiency.
- **SKU field** was added as a realistic unique product identifier, common in inventory management systems.
- **Construction supply data** was used for sample data to align with Remarcable's domain in construction procurement.
- **SQLite** is used as the database for simplicity. No additional database setup is required.
- **Pagination** (10 per page) was added as a best practice, even though not explicitly required, to handle large datasets gracefully.

## AI Attribution

This project was developed with AI assistance (Anthropic Claude) for code generation and documentation. All AI-generated code was reviewed, understood, modified, and tested by the developer. The developer can explain every implementation detail, design decision, and query strategy used in this project.
