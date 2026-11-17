from django.db import models

from orders.models import Order


class Payment(models.Model):
    STATUS_CHOICES = [
        ("initialized", "Initialized"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="initialized")
    authorization_url = models.URLField(blank=True)
    access_code = models.CharField(max_length=100, blank=True)
    paystack_response = models.JSONField(blank=True, null=True)
    refund_reference = models.CharField(max_length=100, blank=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.reference} ({self.status})"
