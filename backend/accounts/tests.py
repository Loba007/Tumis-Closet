from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from .tokens import email_verification_token

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_returns_user_and_tokens(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "ada",
                "email": "ada@example.com",
                "password": "strong-pass-123",
                "first_name": "Ada",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["user"]["email"], "ada@example.com")
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_normalizes_case_and_rejects_case_variant_duplicate(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "ada",
                "email": "Ada@Example.COM",
                "password": "strong-pass-123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["user"]["email"], "ada@example.com")

        duplicate = self.client.post(
            reverse("register"),
            {
                "username": "ada2",
                "email": "ada@example.com",
                "password": "strong-pass-123",
            },
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", duplicate.data)

    def test_login_is_case_insensitive_for_email(self):
        User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        response = self.client.post(
            reverse("login"),
            {"email": "  ADA@Example.com  ", "password": "strong-pass-123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_login_and_logout_blacklists_refresh_token(self):
        User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        login = self.client.post(
            reverse("login"),
            {"email": "ada@example.com", "password": "strong-pass-123"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        access = login.data["access"]
        refresh = login.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout = self.client.post(reverse("logout"), {"refresh": refresh}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_204_NO_CONTENT)

        self.client.credentials()
        refresh_response = self.client.post(
            reverse("login-refresh"), {"refresh": refresh}, format="json"
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_can_be_updated(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )
        self.client.force_authenticate(user)
        response = self.client.patch(
            reverse("me"), {"first_name": "Adaeze", "phone_number": "08012345678"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Adaeze")

class PasswordAndEmailTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ada", email="ada@example.com", password="strong-pass-123"
        )

    @patch("accounts.views.send_email_verification_email")
    def test_register_sends_verification_email(self, send_verification):
        response = self.client.post(
            reverse("register"),
            {
                "username": "bisi",
                "email": "bisi@example.com",
                "password": "strong-pass-123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertFalse(response.data["user"]["email_verified"])
        send_verification.assert_called_once()

    @patch("accounts.views.send_password_reset_email")
    def test_password_reset_request_is_generic_and_sends_for_real_user(self, send_reset):
        response = self.client.post(
            reverse("password-reset"), {"email": "ada@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        send_reset.assert_called_once()

        unknown = self.client.post(
            reverse("password-reset"), {"email": "nobody@example.com"}, format="json"
        )
        self.assertEqual(unknown.status_code, status.HTTP_200_OK)
        self.assertEqual(send_reset.call_count, 1)

    def test_password_reset_confirm_changes_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            reverse("password-reset-confirm"),
            {"uid": uid, "token": token, "new_password": "new-strong-pass-456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-strong-pass-456"))

    def test_email_verification_marks_user_verified(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = email_verification_token.make_token(self.user)
        response = self.client.post(
            reverse("email-verify"), {"uid": uid, "token": token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    @patch("accounts.views.send_email_verification_email")
    def test_resend_verification_requires_authentication(self, send_verification):
        response = self.client.post(reverse("email-resend"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("email-resend"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        send_verification.assert_called_once()
