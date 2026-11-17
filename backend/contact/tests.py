from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ContactMessage


class ContactCreateTests(APITestCase):
    def test_anyone_can_submit_an_enquiry(self):
        response = self.client.post(
            reverse("contact-create"),
            {
                "name": "Ada",
                "email": "ada@example.com",
                "subject": "Bespoke order",
                "message": "I would like a custom gown.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertFalse(ContactMessage.objects.get().is_handled)

    @override_settings(CONTACT_EMAIL="studio@example.com")
    @patch("contact.views.send_mail", side_effect=OSError("SMTP unavailable"))
    def test_enquiry_is_saved_when_studio_notification_fails(self, send_mail):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("contact-create"),
                {
                    "name": "Ada",
                    "email": "ada@example.com",
                    "subject": "Bespoke order",
                    "message": "I would like a custom gown.",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)
        send_mail.assert_called_once()

    def test_message_is_required(self):
        response = self.client.post(
            reverse("contact-create"),
            {"name": "Ada", "email": "ada@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
