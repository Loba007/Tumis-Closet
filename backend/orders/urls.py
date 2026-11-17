from django.urls import path

from .views import (
    CheckoutView,
    OrderCancelView,
    OrderDetailView,
    OrderListView,
    OrderRefundView,
    ShippingQuoteView,
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("shipping-quote/", ShippingQuoteView.as_view(), name="shipping-quote"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<int:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("<int:pk>/refund/", OrderRefundView.as_view(), name="order-refund"),
]
