import logging

from django.contrib import admin, messages
from django.utils import timezone

from payments.paystack_client import PaystackError, refund_transaction

from .models import Order, OrderItem

logger = logging.getLogger(__name__)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number", "user", "status", "shipping_method", "total_amount",
        "stock_reserved", "stock_returned", "refund_required", "refunded_at",
        "created_at",
    ]
    list_filter = ["status", "shipping_method", "stock_returned", "refund_required"]
    search_fields = ["order_number", "user__email"]
    readonly_fields = [
        "order_number", "stock_reserved", "stock_returned", "refund_required",
        "refunded_at", "created_at", "updated_at",
    ]
    inlines = [OrderItemInline]
    actions = ["cancel_and_restock", "refund_captured_payments"]

    @admin.action(description="Cancel selected orders and return stock")
    def cancel_and_restock(self, request, queryset):
        count = 0
        for order in queryset.filter(status__in=["pending", "paid"]):
            order.cancel()
            count += 1
        self.message_user(request, f"Cancelled {count} order(s) and returned stock.")

    @admin.action(description="Refund captured payment via Paystack (full refund)")
    def refund_captured_payments(self, request, queryset):
        refunded = 0
        skipped = 0
        failed = 0
        for order in queryset.select_related("payment"):
            payment = getattr(order, "payment", None)
            if not payment or payment.status != "success":
                skipped += 1
                continue
            try:
                data = refund_transaction(payment.reference)
            except PaystackError:
                logger.exception("Refund failed for order %s", order.order_number)
                failed += 1
                continue

            now = timezone.now()
            payment.status = "refunded"
            payment.refund_reference = str(
                data.get("reference") or data.get("id") or payment.reference
            )
            payment.refunded_at = now
            payment.paystack_response = data
            payment.save(
                update_fields=[
                    "status",
                    "refund_reference",
                    "refunded_at",
                    "paystack_response",
                ]
            )
            order.refund_required = False
            order.refunded_at = now
            order.save(update_fields=["refund_required", "refunded_at"])
            refunded += 1

        level = messages.SUCCESS if failed == 0 else messages.WARNING
        self.message_user(
            request,
            f"Refunded {refunded}; skipped {skipped}; failed {failed}. "
            "Check server logs for provider errors.",
            level=level,
        )
