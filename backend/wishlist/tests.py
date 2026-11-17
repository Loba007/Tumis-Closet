from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Category
from products.models import Product

User = get_user_model()


class WishlistTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        category = Category.objects.create(name="Dresses")
        self.product = Product.objects.create(
            category=category, name="Adire Dress", sku="DRESS-1", price="10000"
        )
        self.client.force_authenticate(self.user)

    def test_add_list_and_remove_wishlist_item(self):
        add = self.client.post(reverse("wishlist"), {"product": self.product.id}, format="json")
        self.assertEqual(add.status_code, status.HTTP_201_CREATED)

        listing = self.client.get(reverse("wishlist"))
        self.assertEqual(len(listing.data), 1)
        self.assertEqual(listing.data[0]["product_detail"]["name"], "Adire Dress")

        remove = self.client.delete(
            reverse("wishlist"), {"product": self.product.id}, format="json"
        )
        self.assertEqual(remove.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(self.client.get(reverse("wishlist")).data), 0)
