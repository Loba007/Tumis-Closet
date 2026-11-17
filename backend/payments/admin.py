from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["reference", "order", "amount", "status", "paid_at", "refunded_at"]
    list_filter = ["status"]
    search_fields = ["reference", "order__order_number"]
    readonly_fields = [
        "order", "reference", "amount", "status", "paystack_response",
        "paid_at", "refund_reference", "refunded_at",
    ]
