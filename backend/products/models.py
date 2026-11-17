import uuid

from django.db import models
from django.utils.text import slugify

from categories.models import Category


class Product(models.Model):
    """A single design. is_portfolio_only lets a piece appear in the
    gallery without being purchasable — useful for showcase/one-off runway
    pieces that aren't part of the shop catalog."""

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_portfolio_only = models.BooleanField(
        default=False, help_text="Show in the portfolio gallery but hide from the shop/cart."
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def in_stock(self):
        return self.variants.filter(stock_quantity__gt=0).exists()

    @property
    def average_rating(self):
        agg = self.reviews.filter(is_approved=True).aggregate(models.Avg("rating"))
        return round(agg["rating__avg"] or 0, 1)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    """Stock is tracked per size/colour combination, since that's how a
    fashion catalog actually sells — not at the product level."""

    SIZE_CHOICES = [
        ("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"),
        ("XL", "XL"), ("XXL", "XXL"), ("FREE", "Free Size"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default="FREE")
    color = models.CharField(max_length=50, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    variant_sku = models.CharField(max_length=60, unique=True)

    class Meta:
        unique_together = ("product", "size", "color")
        ordering = ["size"]

    def __str__(self):
        return f"{self.product.name} — {self.size}/{self.color or 'default'}"
