"""Shipping fee rules.

Rates live here (server-side) so the browser can never choose its own price.
The storefront asks the API for a quote and the checkout recalculates again.
"""

from decimal import Decimal

LAGOS_PREMIUM_AREAS = {
    "lekki",
    "victoria island",
    "vi",
    "ikoyi",
    "ikeja",
    "surulere",
    "yaba",
}

LAGOS_FEE = Decimal("3500")
LAGOS_PREMIUM_FEE = Decimal("2500")
INTERSTATE_FEE = Decimal("5000")


def normalize(value):
    return (value or "").strip().lower()


def calculate_shipping_fee(state, city="", method="delivery"):
    if method == "pickup":
        return Decimal("0")

    state = normalize(state)
    city = normalize(city)

    if "lagos" in state:
        if any(area in city for area in LAGOS_PREMIUM_AREAS):
            return LAGOS_PREMIUM_FEE
        return LAGOS_FEE

    return INTERSTATE_FEE
