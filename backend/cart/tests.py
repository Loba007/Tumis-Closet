from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Category
from products.models import Product, ProductVariant

User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        category = Category.objects.create(name="Dresses")
        self.product = Product.objects.create(
            category=category, name="Adire Dress", sku="DRESS-1", price="10000"
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, size="M", stock_quantity=2, variant_sku="DRESS-1-M"
        )
        self.client.force_authenticate(self.user)

    def test_add_and_update_cart_item(self):
        response = self.client.post(
            reverse("cart-item-add"), {"variant": self.variant.id, "quantity": 2}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["item_count"], 2)

        item_id = response.data["items"][0]["id"]
        update = self.client.patch(
            reverse("cart-item-detail", args=[item_id]), {"quantity": 1}, format="json"
        )
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(update.data["item_count"], 1)

    def test_add_rejects_more_than_stock(self):
        response = self.client.post(
            reverse("cart-item-add"), {"variant": self.variant.id, "quantity": 3}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_portfolio_only_piece_cannot_be_added(self):
        self.product.is_portfolio_only = True
        self.product.save(update_fields=["is_portfolio_only"])
        response = self.client.post(
            reverse("cart-item-add"), {"variant": self.variant.id, "quantity": 1}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
