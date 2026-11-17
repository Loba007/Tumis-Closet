from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Category
from products.models import Product

from .models import Review

User = get_user_model()


class ReviewModerationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        self.other = User.objects.create_user(
            username="bisi", email="bisi@example.com", password="strong-pass-123"
        )
        category = Category.objects.create(name="Dresses")
        self.product = Product.objects.create(
            category=category, name="Adire Dress", sku="DRESS-1", price="10000"
        )

    def test_customer_review_waits_for_approval(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("review-list"),
            {"product": self.product.id, "rating": 5, "comment": "Beautiful."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get()
        self.assertFalse(review.is_approved)
        self.assertFalse(response.data["is_approved"])

        self.client.force_authenticate(self.other)
        listing = self.client.get(reverse("review-list"), {"product": self.product.id})
        self.assertEqual(listing.data["count"], 0)

        self.client.force_authenticate(self.user)
        own_listing = self.client.get(reverse("review-list"), {"product": self.product.id})
        self.assertEqual(own_listing.data["count"], 1)

    def test_staff_review_is_immediately_approved(self):
        staff = User.objects.create_user(
            username="staff", email="staff@example.com", password="strong-pass-123", is_staff=True
        )
        self.client.force_authenticate(staff)
        response = self.client.post(
            reverse("review-list"),
            {"product": self.product.id, "rating": 4, "comment": "Lovely finish."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.get().is_approved)

    def test_customer_edit_sends_review_back_to_moderation(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Original.",
            is_approved=True,
        )
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse("review-detail", args=[review.id]),
            {"rating": 1, "comment": "Changed my mind."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        review.refresh_from_db()
        self.assertFalse(review.is_approved)
