from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from rest_framework import generics, permissions
from rest_framework.throttling import ScopedRateThrottle

from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactCreateView(generics.CreateAPIView):
    """Store an enquiry and, when email is configured, notify the studio."""

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"

    def perform_create(self, serializer):
        message = serializer.save()
        recipient = getattr(settings, "CONTACT_EMAIL", "")
        if recipient:
            transaction.on_commit(
                lambda: send_mail(
                    subject=f"Website enquiry: {message.subject or 'General'}",
                    message=f"From: {message.name} <{message.email}>\n\n{message.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    fail_silently=False,
                ),
                robust=True,
            )
