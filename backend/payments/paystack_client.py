"""
Thin wrapper around the Paystack REST API.

PAYSTACK_SECRET_KEY / PAYSTACK_PUBLIC_KEY are read from settings, which in
turn read from environment variables (see backend/.env.example). Until real
keys are supplied, calls to Paystack will fail — that failure is caught
here and raised as a clean PaystackError instead of a raw exception, so the
view layer can always return a sensible JSON error to the frontend.
"""

from decimal import ROUND_HALF_UP, Decimal

import requests
from django.conf import settings


class PaystackError(Exception):
    pass


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def _request(method, url, **kwargs):
    try:
        response = requests.request(method, url, headers=_headers(), timeout=15, **kwargs)
    except requests.RequestException as exc:
        raise PaystackError(f"Could not reach Paystack: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise PaystackError(
            f"Paystack returned an unexpected response (HTTP {response.status_code}). "
            "Check that PAYSTACK_SECRET_KEY is set correctly in .env."
        ) from exc

    if not isinstance(data, dict):
        raise PaystackError("Paystack returned an unexpected response.")

    if not response.ok or not data.get("status"):
        raise PaystackError(data.get("message", "Paystack request was not successful."))

    result = data.get("data")
    if not isinstance(result, dict):
        raise PaystackError("Paystack returned an incomplete response.")
    return result


def _amount_kobo(amount_naira):
    amount = Decimal(str(amount_naira)) * 100
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def initialize_transaction(email: str, amount_naira, reference: str, callback_url: str = None):
    """Amount must be converted to kobo (Paystack's smallest unit)."""
    payload = {
        "email": email,
        "amount": _amount_kobo(amount_naira),
        "reference": reference,
    }
    if callback_url:
        payload["callback_url"] = callback_url

    return _request("POST", f"{settings.PAYSTACK_BASE_URL}/transaction/initialize", json=payload)
    # returns dict containing authorization_url, access_code, reference


def verify_transaction(reference: str):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    return _request("GET", url)
    # returns dict containing status ("success"/"failed"), amount, etc.


def refund_transaction(reference: str, amount_naira=None):
    payload = {"transaction": reference}
    if amount_naira is not None:
        payload["amount"] = _amount_kobo(amount_naira)
    return _request("POST", f"{settings.PAYSTACK_BASE_URL}/refund", json=payload)
