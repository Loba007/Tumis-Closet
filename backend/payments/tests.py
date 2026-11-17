import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order

from .models import Payment

User = get_user_model()


def make_order(user, total="10000"):
    return Order.objects.create(
        user=user,
        shipping_full_name="Ada Obi",
        shipping_phone_number="08012345678",
        shipping_line1="1 Test Street",
        shipping_city="Lekki",
        shipping_state="Lagos",
        subtotal=Decimal(total),
        total_amount=Decimal(total),
    )


class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        self.order = make_order(self.user)
        self.payment = Payment.objects.create(
            order=self.order,
            reference="TC-PAY-TEST",
            amount=self.order.total_amount,
            status="initialized",
            authorization_url="https://checkout.paystack.com/test",
        )
        self.client.force_authenticate(self.user)

    @patch("payments.views.verify_transaction")
    def test_verify_marks_order_paid_when_amount_matches(self, verify):
        verify.return_value = {
            "status": "success",
            "reference": "TC-PAY-TEST",
            "amount": 1000000,
            "currency": "NGN",
        }
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")

    @patch("payments.views.verify_transaction")
    def test_verify_rejects_amount_mismatch(self, verify):
        verify.return_value = {
            "status": "success",
            "reference": "TC-PAY-TEST",
            "amount": 1,
            "currency": "NGN",
        }
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "pending")

    @patch("payments.views.verify_transaction")
    def test_verify_rejects_missing_provider_reference(self, verify):
        verify.return_value = {
            "status": "success",
            "amount": 1000000,
            "currency": "NGN",
        }
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "pending")

    @patch("payments.views.verify_transaction")
    def test_verify_rejects_missing_provider_currency(self, verify):
        verify.return_value = {
            "status": "success",
            "reference": "TC-PAY-TEST",
            "amount": 1000000,
        }
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "pending")

    @patch("payments.views.verify_transaction")
    def test_verify_rejects_fractional_kobo_amount(self, verify):
        verify.return_value = {
            "status": "success",
            "reference": "TC-PAY-TEST",
            "amount": "1000000.5",
            "currency": "NGN",
        }
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "pending")

    @patch("payments.views.initialize_transaction")
    def test_initialize_reuses_live_checkout_url(self, initialize):
        response = self.client.post(
            reverse("payment-initialize"), {"order_id": self.order.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["authorization_url"], self.payment.authorization_url)
        initialize.assert_not_called()

    @patch("payments.views.initialize_transaction")
    def test_initialize_rejects_non_paystack_checkout_url(self, initialize):
        order = make_order(self.user, total="5000")
        initialize.return_value = {
            "authorization_url": "https://example.com/checkout",
            "access_code": "access",
            "reference": "unused",
        }
        response = self.client.post(
            reverse("payment-initialize"), {"order_id": order.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertFalse(Payment.objects.filter(order=order).exists())

    @patch("payments.views.initialize_transaction")
    def test_initialize_rejects_reference_mismatch(self, initialize):
        order = make_order(self.user, total="5000")
        initialize.return_value = {
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "access",
            "reference": "unexpected-reference",
        }
        response = self.client.post(
            reverse("payment-initialize"), {"order_id": order.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertFalse(Payment.objects.filter(order=order).exists())

    @override_settings(PAYSTACK_SECRET_KEY="sk_test_secret")
    def test_webhook_with_valid_signature_marks_paid(self):
        payload = {
            "event": "charge.success",
            "data": {
                "reference": "TC-PAY-TEST",
                "status": "success",
                "amount": 1000000,
                "currency": "NGN",
            },
        }
        body = json.dumps(payload).encode()
        signature = hmac.new(b"sk_test_secret", body, hashlib.sha512).hexdigest()
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("payment-webhook"),
            data=body,
            content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE=signature,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")

    @override_settings(PAYSTACK_SECRET_KEY="sk_test_secret")
    def test_webhook_rejects_bad_signature(self):
        response = self.client.post(
            reverse("payment-webhook"),
            {"event": "charge.success", "data": {"reference": "TC-PAY-TEST"}},
            format="json",
            HTTP_X_PAYSTACK_SIGNATURE="bad",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "pending")

    @patch("payments.views.verify_transaction")
    def test_verify_requires_payment_ownership(self, verify):
        other = User.objects.create_user(
            username="bisi", email="bisi@example.com", password="strong-pass-123"
        )
        self.client.force_authenticate(other)
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        verify.assert_not_called()

    @patch("payments.views.verify_transaction")
    def test_failed_verification_clears_stale_checkout_url(self, verify):
        verify.return_value = {
            "status": "failed",
            "amount": 1000000,
            "currency": "NGN",
        }
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "failed")
        self.assertEqual(self.payment.authorization_url, "")

    @patch("payments.views.verify_transaction")
    def test_late_success_for_cancelled_order_flags_refund(self, verify):
        self.order.status = "cancelled"
        self.order.save(update_fields=["status"])
        verify.return_value = {
            "status": "success",
            "reference": "TC-PAY-TEST",
            "amount": 1000000,
            "currency": "NGN",
        }
        response = self.client.post(
            reverse("payment-verify"), {"reference": "TC-PAY-TEST"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")
        self.assertTrue(self.order.refund_required)
        self.assertEqual(self.payment.status, "success")
