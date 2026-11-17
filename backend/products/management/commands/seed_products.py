from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from categories.models import Category
from products.models import Product, ProductVariant

DEMO_SKU_PREFIX = "DEMO-"

DEMO_PRODUCTS = [
    {
        "sku": "DEMO-ADUNNI-SLIP",
        "name": "Adunni Slip Dress",
        "category": "Dresses",
        "price": Decimal("85000.00"),
        "description": "A fluid bias-cut slip dress in soft satin, finished with adjustable straps. Dresses up for owambe or down for a quiet Sunday.",
        "is_featured": True,
        "variants": [("XS", 3), ("S", 5), ("M", 4), ("L", 2)],
    },
    {
        "sku": "DEMO-OWAMBE-GOWN",
        "name": "Owambe Statement Gown",
        "category": "Owambe",
        "price": Decimal("145000.00"),
        "discount_price": Decimal("125000.00"),
        "description": "Floor-length statement gown with a structured bodice and dramatic sleeve. Built for the moments that matter.",
        "is_featured": True,
        "variants": [("S", 2), ("M", 3), ("L", 2), ("XL", 1)],
    },
    {
        "sku": "DEMO-IKORODU-MIDI",
        "name": "Ikorodu Linen Midi",
        "category": "Dresses",
        "price": Decimal("68000.00"),
        "description": "Breathable linen midi with a relaxed silhouette and side slit. An everyday Lagos staple.",
        "is_featured": False,
        "variants": [("S", 4), ("M", 6), ("L", 4), ("XL", 2)],
    },
    {
        "sku": "DEMO-BRIDAL-LACE",
        "name": "Bridal Lace Gown",
        "category": "Bridal",
        "price": Decimal("320000.00"),
        "description": "Hand-finished lace bridal gown with a fitted bodice and sweeping train. Made to order in our Lagos studio.",
        "is_featured": False,
        "variants": [("S", 1), ("M", 1), ("L", 1)],
    },
    {
        "sku": "DEMO-ASOOKE-RUNWAY",
        "name": "Aso Oke Runway Set",
        "category": "Owambe",
        "price": Decimal("195000.00"),
        "description": "Handwoven Aso Oke two-piece shown at our 2025 Lagos runway presentation. A showcase piece — enquiries welcome for a bespoke version.",
        "is_featured": False,
        "is_portfolio_only": True,
        "variants": [],
    },
    {
        "sku": "DEMO-ADIRE-SHOWCASE",
        "name": "Adire Showcase Gown",
        "category": "Dresses",
        "price": Decimal("120000.00"),
        "description": "Indigo Adire gown from our studio archive, styled for the lookbook. Not part of the ready-to-wear catalog.",
        "is_featured": False,
        "is_portfolio_only": True,
        "variants": [],
    },
]

DEMO_CATEGORIES = {
    "Dresses": "Ready-to-wear dresses for every occasion.",
    "Owambe": "Statement pieces for weddings and celebrations.",
    "Bridal": "Made-to-order bridal and engagement looks.",
}


class Command(BaseCommand):
    help = "Seed a few demo dresses. Safe to re-run; use --delete to remove them."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Remove all seeded demo products (SKUs starting with DEMO-).",
        )

    def handle(self, *args, **options):
        if options["delete"]:
            return self._delete_demo_products()

        with transaction.atomic():
            for name, description in DEMO_CATEGORIES.items():
                category, _ = Category.objects.get_or_create(
                    name=name, defaults={"description": description}
                )

                for data in DEMO_PRODUCTS:
                    if data["category"] != name:
                        continue
                    product, created = Product.objects.get_or_create(
                        sku=data["sku"],
                        defaults={
                            "name": data["name"],
                            "category": category,
                            "price": data["price"],
                            "discount_price": data.get("discount_price"),
                            "description": data["description"],
                            "is_featured": data["is_featured"],
                            "is_active": True,
                            "is_portfolio_only": data.get("is_portfolio_only", False),
                        },
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created {product.name}"))
                    else:
                        self.stdout.write(f"Skipped existing {product.name}")

                    for size, stock in data["variants"]:
                        ProductVariant.objects.get_or_create(
                            variant_sku=f"{data['sku']}-{size}",
                            defaults={
                                "product": product,
                                "size": size,
                                "stock_quantity": stock,
                            },
                        )

        self.stdout.write(self.style.SUCCESS("Demo catalog ready. Visit /shop."))

    def _delete_demo_products(self):
        products = Product.objects.filter(sku__startswith=DEMO_SKU_PREFIX)
        count = products.count()
        products.delete()

        demo_names = list(DEMO_CATEGORIES.keys())
        Category.objects.filter(name__in=demo_names, products__isnull=True).delete()

        self.stdout.write(self.style.SUCCESS(f"Removed {count} demo product(s)."))
