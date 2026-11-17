from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Category
from reviews.models import Review

from .models import Product

User = get_user_model()


class ProductCatalogTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Dresses")
        self.product = Product.objects.create(
            category=self.category, name="Adire Dress", sku="DRESS-1", price="10000"
        )
        self.portfolio = Product.objects.create(
            category=self.category,
            name="Runway Gown",
            sku="GOWN-1",
            price="50000",
            is_portfolio_only=True,
        )

    def test_catalog_hides_portfolio_only_pieces(self):
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["slug"], self.product.slug)

    def test_portfolio_filter_returns_portfolio_pieces(self):
        response = self.client.get(reverse("product-list"), {"portfolio": "true"})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["slug"], self.portfolio.slug)

    def test_average_rating_only_counts_approved_reviews(self):
        first = User.objects.create_user(
            username="one", email="one@example.com", password="strong-pass-123"
        )
        second = User.objects.create_user(
            username="two", email="two@example.com", password="strong-pass-123"
        )
        Review.objects.create(product=self.product, user=first, rating=5, is_approved=True)
        Review.objects.create(product=self.product, user=second, rating=1, is_approved=False)

        response = self.client.get(reverse("product-detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_rating"], 5.0)

    def test_search_filters_by_name(self):
        Product.objects.create(category=self.category, name="Lace Top", sku="TOP-1", price="8000")
        response = self.client.get(reverse("product-list"), {"search": "lace"})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Lace Top")


class ProductWriteValidationTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Dresses")
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="strong-pass-123",
            is_staff=True,
        )
        self.client.force_authenticate(self.staff)

    def test_rejects_negative_price(self):
        response = self.client.post(
            reverse("product-list"),
            {
                "name": "Bad Price",
                "sku": "BAD-1",
                "price": "-100",
                "category": self.category.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_rejects_discount_above_price(self):
        response = self.client.post(
            reverse("product-list"),
            {
                "name": "Bad Discount",
                "sku": "BAD-2",
                "price": "1000",
                "discount_price": "2000",
                "category": self.category.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("discount_price", response.data)
