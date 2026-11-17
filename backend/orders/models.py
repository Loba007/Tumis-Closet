import uuid

from django.conf import settings
from django.db import models
from django.db.models import F

from products.models import ProductVariant


def generate_order_number():
    return f"TC-{uuid.uuid4().hex[:8].upper()}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    SHIPPING_METHOD_CHOICES = [
        ("delivery", "Delivery"),
        ("pickup", "Studio Pickup"),
    ]

    ALLOWED_TRANSITIONS = {
        "pending": {"paid", "cancelled"},
        "paid": {"processing", "shipped", "cancelled"},
        "processing": {"shipped", "delivered", "cancelled"},
        "shipped": {"delivered"},
        "delivered": set(),
        "cancelled": set(),
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=20, unique=True, default=generate_order_number)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES, default="delivery")

    # Stock is reserved when the order is created and released if the order
    # is cancelled or expires before payment.
    stock_reserved = models.BooleanField(default=False)
    stock_returned = models.BooleanField(default=False)

    # Set when a paid order is cancelled and the customer still needs a refund.
    refund_required = models.BooleanField(default=False)
    refunded_at = models.DateTimeField(blank=True, null=True)

    # Shipping snapshot — copied at checkout time so later address edits
    # don't rewrite history on a placed order.
    shipping_full_name = models.CharField(max_length=150)
    shipping_phone_number = models.CharField(max_length=20)
    shipping_line1 = models.CharField(max_length=255)
    shipping_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100, default="Nigeria")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def release_stock(self):
        """Return reserved stock to inventory exactly once."""
        if not self.stock_reserved or self.stock_returned:
            return
        for item in self.items.all():
            if item.variant_id:
                ProductVariant.objects.filter(pk=item.variant_id).update(
                    stock_quantity=F("stock_quantity") + item.quantity
                )
        self.stock_returned = True
        self.save(update_fields=["stock_returned"])

    def cancel(self):
        """Cancel the order, restock it, and flag any captured payment for refund."""
        self.release_stock()
        self.status = "cancelled"
        fields = ["status"]
        payment = getattr(self, "payment", None)
        if payment and payment.status == "success" and not self.refund_required:
            self.refund_required = True
            fields.append("refund_required")
        self.save(update_fields=fields)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, related_name="order_items")

    # Snapshots so the order stays accurate even if the product is edited/deleted later.
    product_name = models.CharField(max_length=200)
    size = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity
