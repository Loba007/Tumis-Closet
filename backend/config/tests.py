from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from categories.models import Category
from products.models import Product

from . import settings as project_settings


class ProductionConfigurationTests(SimpleTestCase):
    def validate_production_settings(self, **overrides):
        configuration = {
            "DEBUG": False,
            "SECRET_KEY": "A" * 60,
            "DATABASE_URL": "postgres://user:password@db.example.com:5432/closet",
            "ALLOWED_HOSTS": ["api.example.com"],
            "FRONTEND_URL": "https://shop.example.com",
            "CORS_ALLOWED_ORIGINS": ["https://shop.example.com"],
            "CORS_ALLOW_ALL_ORIGINS": False,
            "CSRF_TRUSTED_ORIGINS": ["https://shop.example.com"],
            "PAYSTACK_SECRET_KEY": "sk_live_ci_fake_key_123456789",
            "PAYSTACK_PUBLIC_KEY": "pk_live_ci_fake_key_123456789",
            "PAYSTACK_MODE": "live",
            "ALLOW_TEST_PAYMENTS": False,
            "USE_CLOUDINARY": True,
            "ALLOW_LOCAL_MEDIA": False,
            "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "EMAIL_HOST": "smtp.example.com",
            "CONTACT_EMAIL": "hello@example.com",
            "EMAIL_USE_TLS": True,
            "EMAIL_USE_SSL": False,
            "SECURE_SSL_REDIRECT": True,
            "SESSION_COOKIE_SECURE": True,
            "CSRF_COOKIE_SECURE": True,
            "SECURE_HSTS_SECONDS": 31536000,
        }
        configuration.update(overrides)
        with (
            patch.multiple(project_settings, **configuration),
            patch.dict(
                project_settings.CLOUDINARY_STORAGE,
                {"CLOUD_NAME": "ci", "API_KEY": "123456", "API_SECRET": "ci-secret"},
            ),
        ):
            project_settings._validate_production_settings()

    def test_accepts_valid_live_production_configuration(self):
        self.validate_production_settings()

    def test_rejects_test_keys_for_customer_facing_production(self):
        with self.assertRaisesRegex(ImproperlyConfigured, "Test Paystack keys are blocked"):
            self.validate_production_settings(
                PAYSTACK_SECRET_KEY="sk_test_ci_fake_key_123456789",
                PAYSTACK_PUBLIC_KEY="pk_test_ci_fake_key_123456789",
                PAYSTACK_MODE="test",
            )

    def test_rejects_local_frontend_origins_in_production(self):
        with self.assertRaisesRegex(ImproperlyConfigured, "must not include local origins"):
            self.validate_production_settings(
                CORS_ALLOWED_ORIGINS=[
                    "https://shop.example.com",
                    "http://localhost:5173",
                ]
            )

    def test_rejects_cors_allow_all_in_production(self):
        with self.assertRaisesRegex(ImproperlyConfigured, "CORS_ALLOW_ALL_ORIGINS"):
            self.validate_production_settings(CORS_ALLOW_ALL_ORIGINS=True)

    def test_rejects_ipv6_loopback_as_public_allowed_host(self):
        with self.assertRaisesRegex(ImproperlyConfigured, "must include the public API hostname"):
            self.validate_production_settings(ALLOWED_HOSTS=["::1"])


class HealthAndSitemapTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_sitemap_lists_frontend_product_and_category_urls(self):
        category = Category.objects.create(name="Dresses")
        product = Product.objects.create(
            category=category, name="Adire Dress", sku="DRESS-1", price="10000"
        )

        response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        body = response.content.decode()
        self.assertIn("/product/", body)
        self.assertIn(product.slug, body)
        self.assertIn(f"category={category.slug}", body)
        self.assertIn(project_settings.FRONTEND_URL, body)
