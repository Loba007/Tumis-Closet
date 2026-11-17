from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from orders.models import Order
from payments.models import Payment
from payments.paystack_client import PaystackError, verify_transaction
from payments.views import _mark_failed, _mark_paid


class Command(BaseCommand):
    help = "Cancel unpaid orders older than N minutes and return their reserved stock."

    def add_arguments(self, parser):
        parser.add_argument("--minutes", type=int, default=60)

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=options["minutes"])
        expired = (
            Order.objects.filter(
                status="pending",
                stock_reserved=True,
                stock_returned=False,
                created_at__lt=cutoff,
            )
            .select_related("payment")
            .order_by("id")
        )
        cancelled = 0
        recovered = 0
        skipped = 0

        for order in expired.iterator():
            payment = getattr(order, "payment", None)

            if payment and payment.status == "success":
                Order.objects.filter(pk=order.pk, status="pending").update(status="paid")
                recovered += 1
                continue

            # If the buyer started a Paystack checkout, verify once before
            # cancelling. This avoids restocking an order that was actually
            # paid but whose webhook/redirect never arrived.
            if payment and payment.status == "initialized":
                try:
                    data = verify_transaction(payment.reference)
                except PaystackError:
                    skipped += 1
                    continue
                if data.get("status") == "success":
                    try:
                        _mark_paid(payment, data)
                        recovered += 1
                    except PaystackError:
                        skipped += 1
                    continue

            with transaction.atomic():
                locked_payment = (
                    Payment.objects.select_for_update()
                    .filter(order_id=order.pk)
                    .first()
                )
                locked = (
                    Order.objects.select_for_update()
                    .filter(pk=order.pk, status="pending")
                    .first()
                )
                if not locked:
                    continue
                if locked_payment and locked_payment.status == "initialized":
                    _mark_failed(locked_payment)
                locked.cancel()
                cancelled += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Cancelled and restocked {cancelled} expired order(s); "
                f"recovered {recovered} paid order(s); skipped {skipped} pending verification."
            )
        )
