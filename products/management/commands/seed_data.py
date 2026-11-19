"""
Management command to seed the database with sample product data.

This command populates the database with construction/building supply
data: 6 categories, 12 tags, and 24 products — exceeding the minimum
requirements of 5 categories, 10 tags, and 20 products.

Usage:
    python manage.py seed_data

The command is idempotent: running it multiple times will not create
duplicate entries because it uses get_or_create() for categories and
tags, and checks for existing SKUs before creating products.

Note: The assignment specifies using the Django admin to populate data.
      This command is provided as a convenience for reviewers to quickly
      set up sample data. Data can also be entered manually via /admin/.
"""

from django.core.management.base import BaseCommand

from products.models import Category, Product, Tag


class Command(BaseCommand):
    """Seed the database with sample construction supply product data."""

    help = "Populates the database with sample categories, tags, and products."

    def handle(self, *args, **options):
        """Execute the seed data command."""
        self.stdout.write("Seeding database...")

        # --- Create Categories ---
        # Using get_or_create to make the command idempotent (safe to re-run).
        # get_or_create returns a tuple: (object, created_bool)
        categories = {}
        category_names = [
            "Plumbing Supplies",
            "Electrical Equipment",
            "Building Materials",
            "Safety Equipment",
            "HVAC Systems",
            "Tools & Hardware",
        ]
        for name in category_names:
            obj, created = Category.objects.get_or_create(name=name)
            categories[name] = obj
            status = "Created" if created else "Exists"
            self.stdout.write(f"  Category: {name} [{status}]")

        # --- Create Tags ---
        tags = {}
        tag_names = [
            "Industrial",
            "Residential",
            "Commercial",
            "Heavy-Duty",
            "Energy-Efficient",
            "Eco-Friendly",
            "Premium",
            "Budget-Friendly",
            "Bulk",
            "Certified",
            "Weatherproof",
            "Fire-Resistant",
        ]
        for name in tag_names:
            obj, created = Tag.objects.get_or_create(name=name)
            tags[name] = obj
            status = "Created" if created else "Exists"
            self.stdout.write(f"  Tag: {name} [{status}]")

        # --- Create Products ---
        # Each product definition includes: name, description, price, sku,
        # category key, and a list of tag keys.
        product_data = [
            {
                "name": "Copper Pipe 1/2 inch",
                "description": "High-quality copper pipe for residential and commercial plumbing. Corrosion-resistant with excellent thermal conductivity. Suitable for hot and cold water supply lines.",
                "price": 12.99,
                "sku": "PLM-COP-050",
                "category": "Plumbing Supplies",
                "tags": ["Residential", "Commercial", "Premium"],
            },
            {
                "name": "PVC Elbow Fitting 90°",
                "description": "Durable PVC elbow fitting for changing pipe direction. Schedule 40 rated for standard pressure applications. Easy solvent-weld installation.",
                "price": 2.49,
                "sku": "PLM-PVC-901",
                "category": "Plumbing Supplies",
                "tags": ["Residential", "Budget-Friendly"],
            },
            {
                "name": "Brass Ball Valve 3/4 inch",
                "description": "Full-port brass ball valve for reliable shutoff control. Lead-free construction meets NSF/ANSI 61 certification standards. Quarter-turn operation for quick shutoff.",
                "price": 18.75,
                "sku": "PLM-BRS-075",
                "category": "Plumbing Supplies",
                "tags": ["Certified", "Commercial", "Heavy-Duty"],
            },
            {
                "name": "Submersible Sump Pump",
                "description": "Powerful submersible pump for basement water removal. 1/3 HP motor with automatic float switch. Handles up to 2500 gallons per hour.",
                "price": 149.99,
                "sku": "PLM-PMP-033",
                "category": "Plumbing Supplies",
                "tags": ["Residential", "Heavy-Duty", "Certified"],
            },
            {
                "name": "LED Panel Light 2x4",
                "description": "Energy-efficient LED flat panel for commercial ceiling installations. 50W output replaces 150W fluorescent fixtures. 50,000 hour rated lifespan with minimal maintenance.",
                "price": 54.99,
                "sku": "ELC-LED-240",
                "category": "Electrical Equipment",
                "tags": ["Commercial", "Energy-Efficient", "Eco-Friendly"],
            },
            {
                "name": "Circuit Breaker 20A",
                "description": "Single-pole 20-amp circuit breaker for residential electrical panels. UL listed with thermal-magnetic trip mechanism. Plug-in design for quick installation.",
                "price": 8.99,
                "sku": "ELC-BRK-020",
                "category": "Electrical Equipment",
                "tags": ["Residential", "Certified"],
            },
            {
                "name": "Conduit EMT 3/4 inch x 10ft",
                "description": "Galvanized steel electrical metallic tubing for wire protection. Lightweight yet durable for indoor commercial and industrial wiring runs.",
                "price": 6.75,
                "sku": "ELC-EMT-075",
                "category": "Electrical Equipment",
                "tags": ["Industrial", "Commercial", "Bulk"],
            },
            {
                "name": "Industrial Wire Spool 12 AWG",
                "description": "500-foot spool of stranded copper wire for heavy-duty electrical installations. THHN/THWN-2 rated for wet and dry locations. Available in multiple colors.",
                "price": 89.50,
                "sku": "ELC-WIR-012",
                "category": "Electrical Equipment",
                "tags": ["Industrial", "Bulk", "Heavy-Duty"],
            },
            {
                "name": "Portland Cement 94lb Bag",
                "description": "Type I/II Portland cement for general construction purposes. Meets ASTM C150 standards. Ideal for concrete, mortar, and stucco applications.",
                "price": 13.50,
                "sku": "BLD-CEM-094",
                "category": "Building Materials",
                "tags": ["Industrial", "Bulk", "Certified"],
            },
            {
                "name": "Plywood Sheet 4x8 3/4 inch",
                "description": "CDX rated plywood sheet for structural sheathing and subfloor applications. Exposure 1 rated for temporary weather resistance during construction.",
                "price": 42.99,
                "sku": "BLD-PLY-348",
                "category": "Building Materials",
                "tags": ["Residential", "Commercial", "Bulk"],
            },
            {
                "name": "Fiberglass Insulation R-19",
                "description": "Kraft-faced fiberglass batt insulation for exterior wall cavities. R-19 thermal resistance for energy-efficient temperature regulation. Easy friction-fit installation.",
                "price": 38.99,
                "sku": "BLD-INS-R19",
                "category": "Building Materials",
                "tags": ["Residential", "Energy-Efficient", "Eco-Friendly"],
            },
            {
                "name": "Steel Rebar #4 20ft",
                "description": "Grade 60 deformed steel reinforcing bar for concrete reinforcement. #4 (1/2 inch diameter) is common for residential foundations and slabs.",
                "price": 11.25,
                "sku": "BLD-RBR-420",
                "category": "Building Materials",
                "tags": ["Industrial", "Heavy-Duty", "Bulk"],
            },
            {
                "name": "Drywall Sheet 4x8 1/2 inch",
                "description": "Standard gypsum drywall for interior wall and ceiling finishing. Fire-resistant core with recycled paper facing. Lightweight for easier handling.",
                "price": 14.25,
                "sku": "BLD-DRW-048",
                "category": "Building Materials",
                "tags": ["Residential", "Fire-Resistant", "Budget-Friendly"],
            },
            {
                "name": "Hard Hat - Class E",
                "description": "ANSI Z89.1 rated hard hat with electrical insulation up to 20,000V. Ratchet suspension system for adjustable comfortable fit. High-visibility yellow.",
                "price": 24.99,
                "sku": "SAF-HAT-CLE",
                "category": "Safety Equipment",
                "tags": ["Industrial", "Certified", "Heavy-Duty"],
            },
            {
                "name": "Safety Vest Hi-Vis Class 2",
                "description": "ANSI/ISEA 107 Class 2 high-visibility safety vest with reflective strips. Mesh fabric for breathability in hot conditions. Multiple pockets for tools.",
                "price": 12.99,
                "sku": "SAF-VST-CL2",
                "category": "Safety Equipment",
                "tags": ["Industrial", "Commercial", "Certified"],
            },
            {
                "name": "Fall Protection Harness",
                "description": "Full-body fall protection harness with dorsal D-ring. OSHA compliant for workers at heights above 6 feet. Adjustable leg and chest straps.",
                "price": 89.99,
                "sku": "SAF-HAR-FBD",
                "category": "Safety Equipment",
                "tags": ["Industrial", "Certified", "Premium", "Heavy-Duty"],
            },
            {
                "name": "Fire Extinguisher 10lb ABC",
                "description": "Multi-purpose dry chemical fire extinguisher rated for Class A, B, and C fires. Wall-mount bracket included. Annual inspection tag attached.",
                "price": 54.50,
                "sku": "SAF-FEX-010",
                "category": "Safety Equipment",
                "tags": ["Commercial", "Certified", "Fire-Resistant"],
            },
            {
                "name": "Split System AC 3-Ton",
                "description": "Energy-efficient split system air conditioner with 16 SEER rating. R-410A refrigerant for eco-friendly operation. Includes indoor evaporator and outdoor condenser.",
                "price": 2499.00,
                "sku": "HVC-SAC-030",
                "category": "HVAC Systems",
                "tags": ["Residential", "Energy-Efficient", "Eco-Friendly", "Premium"],
            },
            {
                "name": "Commercial Exhaust Fan 24 inch",
                "description": "Heavy-duty exhaust fan for warehouse and commercial ventilation. Direct-drive motor for low maintenance. Weatherproof housing with bird screen.",
                "price": 345.00,
                "sku": "HVC-EXF-024",
                "category": "HVAC Systems",
                "tags": ["Commercial", "Industrial", "Weatherproof", "Heavy-Duty"],
            },
            {
                "name": "Ductwork Galvanized 12 inch",
                "description": "Round galvanized steel ductwork for HVAC air distribution. 26-gauge steel with snap-lock seam. 5-foot sections for flexible layout planning.",
                "price": 28.75,
                "sku": "HVC-DCT-012",
                "category": "HVAC Systems",
                "tags": ["Commercial", "Industrial", "Bulk"],
            },
            {
                "name": "Cordless Drill 20V Max",
                "description": "Professional-grade cordless drill/driver with brushless motor. 20V lithium-ion battery delivers up to 500 in-lbs torque. Includes two batteries and charger.",
                "price": 159.99,
                "sku": "TLS-DRL-020",
                "category": "Tools & Hardware",
                "tags": ["Premium", "Heavy-Duty"],
            },
            {
                "name": "Tape Measure 25ft",
                "description": "Heavy-duty tape measure with magnetic hook and nylon-coated blade. True-zero hook for accurate inside and outside measurements. Belt clip included.",
                "price": 14.99,
                "sku": "TLS-TPM-025",
                "category": "Tools & Hardware",
                "tags": ["Budget-Friendly", "Heavy-Duty"],
            },
            {
                "name": "Laser Level Self-Leveling",
                "description": "360-degree self-leveling rotary laser level for precise alignment. Indoor and outdoor use with pulse mode for detector compatibility. Tripod mount included.",
                "price": 219.00,
                "sku": "TLS-LSR-360",
                "category": "Tools & Hardware",
                "tags": ["Premium", "Certified", "Weatherproof"],
            },
            {
                "name": "Concrete Mixer 3.5 cu ft",
                "description": "Portable electric concrete mixer for small to medium batch jobs. Steel drum with paddle mixing for consistent results. 1/2 HP motor with tilt-to-pour design.",
                "price": 299.99,
                "sku": "TLS-MXR-035",
                "category": "Tools & Hardware",
                "tags": ["Industrial", "Heavy-Duty", "Bulk"],
            },
        ]

        created_count = 0
        for item in product_data:
            # Check if product already exists (by SKU) to maintain idempotency
            if Product.objects.filter(sku=item["sku"]).exists():
                self.stdout.write(f"  Product: {item['name']} [Exists]")
                continue

            product = Product.objects.create(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                sku=item["sku"],
                category=categories[item["category"]],
            )
            # Add tags via the M2M relationship using set() with tag objects
            product_tags = [tags[tag_name] for tag_name in item["tags"]]
            product.tags.set(product_tags)
            created_count += 1
            self.stdout.write(f"  Product: {item['name']} [Created]")

        # --- Summary ---
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Database seeded with "
                f"{Category.objects.count()} categories, "
                f"{Tag.objects.count()} tags, "
                f"{Product.objects.count()} products."
            )
        )
