import hashlib
import hmac
import logging
import uuid
from decimal import Decimal
from urllib.parse import urlparse

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .models import Payment
from .paystack_client import PaystackError, initialize_transaction, verify_transaction
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)


def _amount_matches(payment, data):
    expected_kobo = int(Decimal(payment.amount) * 100)
    try:
        amount = Decimal(str(data.get("amount")))
    except (ArithmeticError, TypeError, ValueError):
        return False
    return amount.is_finite() and amount == amount.to_integral_value() and expected_kobo == int(amount)


def _mark_paid(payment, data):
    """Validate the Paystack amount and mark both payment and order paid.

    A success that arrives for an already-cancelled order is still recorded,
    but the order stays cancelled and is flagged for a manual refund.
    """
    if data.get("status") != "success":
        raise PaystackError("Paystack has not confirmed this transaction as successful.")
    if data.get("reference") != payment.reference:
        raise PaystackError("Payment reference mismatch.")
    if not _amount_matches(payment, data):
        raise PaystackError("Payment amount does not match the order total.")
    if data.get("currency") != "NGN":
        raise PaystackError(f"Unsupported currency: {data.get('currency')}.")

    payment.paystack_response = data
    payment.status = "success"
    payment.paid_at = payment.paid_at or timezone.now()
    payment.save()

    order = payment.order
    if order.status == "pending":
        claimed = Order.objects.filter(pk=order.pk, status="pending").update(
            status="paid"
        )
        order.refresh_from_db(fields=["status", "refund_required"])
        if not claimed and order.status == "cancelled":
            _flag_order_for_refund(order, payment)
    elif order.status == "cancelled":
        _flag_order_for_refund(order, payment)

    payment.order = order
    return payment


def _flag_order_for_refund(order, payment):
    flagged = Order.objects.filter(pk=order.pk, refund_required=False).update(
        refund_required=True
    )
    if flagged:
        order.refund_required = True
        logger.warning(
            "Late payment %s succeeded for cancelled order %s; refund required.",
            payment.reference,
            order.order_number,
        )


def _mark_failed(payment, data=None):
    payment.status = "failed"
    if data is not None:
        payment.paystack_response = data
    payment.authorization_url = ""
    payment.access_code = ""
    payment.save(
        update_fields=[
            "status",
            "paystack_response",
            "authorization_url",
            "access_code",
        ]
    )
    return payment


class InitializePaymentView(APIView):
    """Starts (or resumes) a Paystack transaction for a pending order."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if settings.REQUIRE_EMAIL_VERIFICATION and not request.user.email_verified:
            return Response(
                {
                    "detail": "Verify your email address before starting payment.",
                    "code": "email_unverified",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        order_id = request.data.get("order_id")
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if order.status != "pending":
            return Response(
                {"detail": "Order is not awaiting payment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = Payment.objects.filter(order=order).first()
        if existing and existing.status in ("success", "refunded"):
            return Response(
                {"detail": "This order has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Reuse a live checkout URL instead of creating a second transaction.
        if existing and existing.authorization_url:
            return Response(
                {
                    "authorization_url": existing.authorization_url,
                    "access_code": existing.access_code,
                    "reference": existing.reference,
                    "public_key": settings.PAYSTACK_PUBLIC_KEY,
                }
            )

        reference = f"TC-PAY-{uuid.uuid4().hex[:10].upper()}"
        try:
            data = initialize_transaction(
                email=request.user.email,
                amount_naira=order.total_amount,
                reference=reference,
                callback_url=f"{settings.FRONTEND_URL}/orders/{order.id}",
            )
        except PaystackError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        authorization_url = data.get("authorization_url", "")
        try:
            checkout_url = urlparse(authorization_url)
            valid_checkout_response = (
                data.get("reference") == reference
                and checkout_url.scheme == "https"
                and checkout_url.hostname == "checkout.paystack.com"
                and not checkout_url.username
                and not checkout_url.password
            )
        except (TypeError, ValueError):
            valid_checkout_response = False

        if not valid_checkout_response:
            logger.error("Paystack returned an invalid checkout response for order %s.", order.id)
            return Response(
                {"detail": "The payment provider returned an invalid checkout response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payment, _ = Payment.objects.update_or_create(
            order=order,
            defaults={
                "reference": reference,
                "amount": order.total_amount,
                "status": "initialized",
                "authorization_url": authorization_url,
                "access_code": data.get("access_code", ""),
                "paystack_response": None,
                "paid_at": None,
                "refund_reference": "",
                "refunded_at": None,
            },
        )
        return Response(
            {
                "authorization_url": payment.authorization_url,
                "access_code": payment.access_code,
                "reference": payment.reference,
                "public_key": settings.PAYSTACK_PUBLIC_KEY,
            }
        )


class VerifyPaymentView(APIView):
    """Confirm a Paystack transaction after the redirect back to the site."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        reference = request.data.get("reference")
        if not reference:
            return Response(
                {"detail": "A payment reference is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payments = Payment.objects.select_related("order").filter(reference=reference)
        if not request.user.is_staff:
            payments = payments.filter(order__user=request.user)
        payment = payments.first()
        if not payment:
            return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        if payment.status in ("success", "refunded"):
            return Response(PaymentSerializer(payment).data)

        try:
            data = verify_transaction(reference)
        except PaystackError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        with transaction.atomic():
            payment = (
                Payment.objects.select_for_update()
                .select_related("order")
                .get(pk=payment.pk)
            )
            if payment.status in ("success", "refunded"):
                return Response(PaymentSerializer(payment).data)
            if data.get("status") != "success":
                payment = _mark_failed(payment, data)
            else:
                try:
                    payment = _mark_paid(payment, data)
                except PaystackError as exc:
                    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PaymentSerializer(payment).data)


class PaystackWebhookView(APIView):
    """Server-to-server confirmation, so orders are paid even if the buyer
    closes the browser before the redirect finishes."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        if not settings.PAYSTACK_SECRET_KEY:
            logger.error("Paystack webhook received but PAYSTACK_SECRET_KEY is not set.")
            return Response(
                {"detail": "Payment provider is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        signature = request.headers.get("X-Paystack-Signature", "")
        expected = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            request.body,
            hashlib.sha512,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return Response(
                {"detail": "Invalid signature."}, status=status.HTTP_401_UNAUTHORIZED
            )

        event = request.data.get("event")
        data = request.data.get("data") or {}
        if event != "charge.success":
            return Response({"detail": "Ignored."})

        reference = data.get("reference")
        payment = Payment.objects.select_related("order").filter(reference=reference).first()
        if not payment:
            logger.warning("Paystack webhook referenced unknown payment %s", reference)
            return Response({"detail": "ok"})
        if payment.status in ("success", "refunded"):
            return Response({"detail": "ok"})

        with transaction.atomic():
            locked = (
                Payment.objects.select_for_update()
                .select_related("order")
                .get(pk=payment.pk)
            )
            try:
                _mark_paid(locked, data)
            except PaystackError as exc:
                logger.warning(
                    "Paystack webhook rejected for %s: %s", reference, exc
                )
                return Response(
                    {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response({"detail": "ok"})
