from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Address
from cart.models import Cart, CartItem
from categories.models import Category
from payments.models import Payment
from products.models import Product, ProductVariant

from .models import Order

User = get_user_model()


class OrderTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        category = Category.objects.create(name="Dresses")
        self.product = Product.objects.create(
            category=category, name="Adire Dress", sku="DRESS-1", price=Decimal("10000")
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, size="M", stock_quantity=3, variant_sku="DRESS-1-M"
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, variant=self.variant, quantity=2)
        self.client.force_authenticate(self.user)

    def checkout_payload(self, **overrides):
        payload = {
            "full_name": "Ada Obi",
            "phone_number": "08012345678",
            "line1": "1 Test Street",
            "city": "Lekki",
            "state": "Lagos",
            "country": "Nigeria",
            "shipping_method": "delivery",
        }
        payload.update(overrides)
        return payload


class ShippingQuoteTests(APITestCase):
    def test_lagos_premium_delivery(self):
        response = self.client.post(
            reverse("shipping-quote"),
            {"state": "Lagos", "city": "Lekki", "shipping_method": "delivery"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data["shipping_fee"]), Decimal("2500"))

    def test_interstate_delivery(self):
        response = self.client.post(
            reverse("shipping-quote"),
            {"state": "Abuja", "city": "Wuse", "shipping_method": "delivery"},
            format="json",
        )
        self.assertEqual(Decimal(response.data["shipping_fee"]), Decimal("5000"))

    def test_pickup_is_free(self):
        response = self.client.post(
            reverse("shipping-quote"),
            {"state": "Lagos", "city": "Ikorodu", "shipping_method": "pickup"},
            format="json",
        )
        self.assertEqual(Decimal(response.data["shipping_fee"]), Decimal("0"))


class CheckoutTests(OrderTestCase):
    def test_checkout_ignores_client_shipping_fee_and_reserves_stock(self):
        response = self.client.post(
            reverse("checkout"),
            self.checkout_payload(shipping_fee="1"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        order = Order.objects.get()
        self.assertEqual(order.subtotal, Decimal("20000"))
        self.assertEqual(order.shipping_fee, Decimal("2500"))
        self.assertEqual(order.total_amount, Decimal("22500"))
        self.assertTrue(order.stock_reserved)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 1)
        self.assertFalse(self.cart.items.exists())

    def test_checkout_blocks_insufficient_stock(self):
        CartItem.objects.filter(cart=self.cart).update(quantity=4)
        response = self.client.post(reverse("checkout"), self.checkout_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Order.objects.exists())
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)

    def test_pickup_does_not_require_an_address(self):
        response = self.client.post(
            reverse("checkout"),
            {"shipping_method": "pickup"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Order.objects.get().shipping_fee, Decimal("0"))

    def test_cancel_returns_stock_once(self):
        order = self.client.post(
            reverse("checkout"), self.checkout_payload(), format="json"
        ).data
        response = self.client.post(reverse("order-cancel", args=[order["id"]]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)

        second = self.client.post(reverse("order-cancel", args=[order["id"]]))
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)

    def test_cannot_cancel_after_payment_has_started(self):
        order = self.client.post(
            reverse("checkout"), self.checkout_payload(), format="json"
        ).data
        Payment.objects.create(
            order_id=order["id"],
            reference="TC-PAY-ACTIVE",
            amount=Decimal("22500"),
            status="initialized",
        )
        response = self.client.post(reverse("order-cancel", args=[order["id"]]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 1)

    def test_customer_cannot_see_another_customers_order(self):
        other = User.objects.create_user(
            username="bisi", email="bisi@example.com", password="strong-pass-123"
        )
        order = Order.objects.create(
            user=other,
            shipping_full_name="Bisi",
            shipping_phone_number="08000000000",
            shipping_line1="2 Other Street",
            shipping_city="Ikeja",
            shipping_state="Lagos",
            subtotal=Decimal("1000"),
            total_amount=Decimal("1000"),
        )
        response = self.client.get(reverse("order-detail", args=[order.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CheckoutIntegrityTests(OrderTestCase):
    @override_settings(REQUIRE_EMAIL_VERIFICATION=True)
    def test_checkout_requires_verified_email_when_enabled(self):
        response = self.client.post(reverse("checkout"), self.checkout_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "email_unverified")
        self.assertFalse(Order.objects.exists())
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)

    def test_pickup_never_copies_a_saved_home_address(self):
        address = Address.objects.create(
            user=self.user,
            full_name="Ada Obi",
            phone_number="08012345678",
            line1="1 Private Home Street",
            city="Lekki",
            state="Lagos",
        )
        response = self.client.post(
            reverse("checkout"),
            {"shipping_method": "pickup", "address_id": address.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        order = Order.objects.get()
        self.assertEqual(order.shipping_line1, "Tunmis Closet Studio pickup")
        self.assertNotIn("Private Home", order.shipping_line1)
        self.assertEqual(order.shipping_city, "Ikorodu")

    def test_checkout_blocks_portfolio_only_products(self):
        self.product.is_portfolio_only = True
        self.product.save(update_fields=["is_portfolio_only"])
        response = self.client.post(reverse("checkout"), self.checkout_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Order.objects.exists())


class OrderLifecycleTests(OrderTestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="strong-pass-123",
            is_staff=True,
        )
        order_data = self.client.post(
            reverse("checkout"), self.checkout_payload(), format="json"
        ).data
        self.order = Order.objects.get(pk=order_data["id"])

    def test_staff_cannot_skip_the_order_lifecycle(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(
            reverse("order-detail", args=[self.order.id]),
            {"status": "shipped"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(
            reverse("order-detail", args=[self.order.id]),
            {"status": "paid"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")

    @patch("orders.views.refund_transaction")
    def test_cancelling_paid_order_flags_and_processes_refund(self, refund):
        refund.return_value = {"reference": "REFUND-123"}
        Payment.objects.create(
            order=self.order,
            reference="TC-PAY-PAID",
            amount=self.order.total_amount,
            status="success",
        )
        self.client.force_authenticate(self.staff)

        cancel = self.client.patch(
            reverse("order-detail", args=[self.order.id]),
            {"status": "cancelled"},
            format="json",
        )
        self.assertEqual(cancel.status_code, status.HTTP_200_OK, cancel.data)
        self.order.refresh_from_db()
        self.assertTrue(self.order.refund_required)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)

        refunded = self.client.post(reverse("order-refund", args=[self.order.id]))
        self.assertEqual(refunded.status_code, status.HTTP_200_OK, refunded.data)
        self.order.refresh_from_db()
        self.order.payment.refresh_from_db()
        self.assertFalse(self.order.refund_required)
        self.assertIsNotNone(self.order.refunded_at)
        self.assertEqual(self.order.payment.status, "refunded")
