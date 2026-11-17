import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(subject, body, recipient):
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Could not send account email to %s", recipient)


def send_password_reset_email(user, uid, token):
    query = urlencode({"uid": uid, "token": token})
    link = f"{settings.FRONTEND_URL}/reset-password?{query}"
    _send(
        "Reset your Tunmis Closet password",
        (
            "We received a request to reset your Tunmis Closet password.\n\n"
            f"Choose a new password here: {link}\n\n"
            "This link expires in one hour. If you did not request this, "
            "you can safely ignore this email."
        ),
        user.email,
    )


def send_email_verification_email(user, uid, token):
    query = urlencode({"uid": uid, "token": token})
    link = f"{settings.FRONTEND_URL}/verify-email?{query}"
    _send(
        "Verify your Tunmis Closet email",
        (
            "Welcome to Tunmis Closet.\n\n"
            f"Confirm your email address here: {link}\n\n"
            "This link expires in three days. If you did not create an "
            "account, you can safely ignore this email."
        ),
        user.email,
    )
