from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from payments.models import Payment
from payments.paystack_client import PaystackError, refund_transaction
from products.models import ProductVariant

from .models import Order, OrderItem
from .notifications import send_order_confirmation
from .serializers import (
    CheckoutSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    ShippingQuoteSerializer,
)
from .shipping import calculate_shipping_fee


class OrderListView(generics.ListAPIView):
    """Customers see their own orders; staff see every order (for the
    admin dashboard's order management view)."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("payment").prefetch_related("items")
        if user.is_staff:
            return qs
        return qs.filter(user=user)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("payment").prefetch_related("items")
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only studio staff can update orders."},
                status=status.HTTP_403_FORBIDDEN,
            )
        order = self.get_object()
        order = Order.objects.select_for_update().get(pk=order.pk)
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data.get("status", order.status)

        if new_status != order.status:
            allowed = Order.ALLOWED_TRANSITIONS.get(order.status, set())
            if new_status not in allowed:
                return Response(
                    {
                        "detail": (
                            f"Cannot move an order from {order.status} "
                            f"to {new_status}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if new_status == "cancelled":
                order.cancel()
            else:
                order.status = new_status
                order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data)


class OrderRefundView(APIView):
    """Staff-only full refund for a captured Paystack payment."""

    permission_classes = [permissions.IsAdminUser]

    @transaction.atomic
    def post(self, request, pk):
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .filter(order_id=pk)
            .first()
        )
        if not payment:
            if not Order.objects.filter(pk=pk).exists():
                return Response(
                    {"detail": "Order not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"detail": "This order has no captured payment to refund."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order = Order.objects.select_for_update().get(pk=pk)
        if payment.status != "success":
            return Response(
                {"detail": "This order has no captured payment to refund."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = refund_transaction(payment.reference)
        except PaystackError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

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
        return Response(OrderSerializer(order).data)


class OrderCancelView(APIView):
    """Customers can cancel an unpaid order, returning its stock."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        order = (
            Order.objects.select_for_update()
            .filter(pk=pk, user=request.user)
            .first()
        )
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if order.status != "pending":
            return Response(
                {"detail": "Only unpaid orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment = getattr(order, "payment", None)
        if payment and payment.status in ("initialized", "success"):
            return Response(
                {
                    "detail": (
                        "A payment has already been started for this order. "
                        "Complete it, or contact the studio if you need help."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.cancel()
        return Response(OrderSerializer(order).data)


class ShippingQuoteView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ShippingQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        fee = calculate_shipping_fee(
            data.get("state", ""),
            data.get("city", ""),
            data.get("shipping_method", "delivery"),
        )
        return Response({"shipping_fee": fee, "currency": "NGN"})


class CheckoutView(APIView):
    """Turns the current cart into an Order. Stock is reserved here;
    the order starts 'pending' until payment is verified."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        if settings.REQUIRE_EMAIL_VERIFICATION and not request.user.email_verified:
            return Response(
                {
                    "detail": (
                        "Verify your email address before checking out. "
                        "You can resend the verification email from your account."
                    ),
                    "code": "email_unverified",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        cart = (
            Cart.objects.select_for_update()
            .filter(user=request.user)
            .prefetch_related("items__variant__product")
            .first()
        )
        if not cart or not cart.items.exists():
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        checkout = CheckoutSerializer(data=request.data)
        checkout.is_valid(raise_exception=True)
        shipping = checkout.resolve_address(request.user)
        shipping_method = checkout.validated_data.get("shipping_method", "delivery")
        shipping_fee = calculate_shipping_fee(
            shipping["shipping_state"], shipping["shipping_city"], shipping_method
        )

        items = list(cart.items.select_related("variant", "variant__product").order_by("variant_id"))
        variant_ids = [item.variant_id for item in items]
        locked_variants = {
            variant.id: variant
            for variant in ProductVariant.objects.select_for_update()
            .filter(id__in=variant_ids)
            .select_related("product")
            .order_by("id")
        }

        subtotal = Decimal("0")
        line_prices = {}
        for item in items:
            variant = locked_variants.get(item.variant_id)
            if not variant:
                return Response(
                    {"detail": "A piece in your bag is no longer available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not variant.product.is_active or variant.product.is_portfolio_only:
                return Response(
                    {
                        "detail": (
                            f"{variant.product.name} is no longer available "
                            "for purchase."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if item.quantity <= 0 or variant.stock_quantity < item.quantity:
                return Response(
                    {
                        "detail": (
                            f"Not enough stock for {variant.product.name} "
                            f"({variant.size})."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            line_prices[variant.id] = variant.product.current_price
            subtotal += line_prices[variant.id] * item.quantity

        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_amount=subtotal + shipping_fee,
            shipping_method=shipping_method,
            stock_reserved=True,
            **shipping,
        )

        for item in items:
            variant = locked_variants[item.variant_id]
            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                size=variant.size,
                color=variant.color,
                quantity=item.quantity,
                price_at_purchase=line_prices[variant.id],
            )
            variant.stock_quantity -= item.quantity
            variant.save(update_fields=["stock_quantity"])

        cart.items.all().delete()
        transaction.on_commit(lambda: send_order_confirmation(order), robust=True)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
