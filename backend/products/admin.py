from django.contrib import admin, messages

from .models import Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 2
    verbose_name_plural = "Sizes & stock"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "price",
        "discount_price",
        "stock_status",
        "is_portfolio_only",
        "is_featured",
        "is_active",
    ]
    list_filter = ["is_portfolio_only", "is_featured", "is_active", "category"]
    search_fields = ["name", "sku"]
    inlines = [ProductImageInline, ProductVariantInline]

    @admin.display(description="Stock")
    def stock_status(self, obj):
        if obj.is_portfolio_only:
            return "Portfolio piece"
        variants = list(obj.variants.all())
        if not variants:
            return "No sizes/stock"
        total = sum(variant.stock_quantity for variant in variants)
        return f"{total} in stock" if total else "Sold Out"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        product = form.instance
        if not product.is_portfolio_only and not product.variants.exists():
            self.message_user(
                request,
                (
                    f"{product.name} has no sizes/stock rows, so it will show as "
                    "Sold Out on the shop. Add at least one size under "
                    "'Sizes & stock'."
                ),
                level=messages.WARNING,
            )
