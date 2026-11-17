from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AddressDetailView,
    AddressListCreateView,
    EmailVerificationConfirmView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendEmailVerificationView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "email/verify/",
        EmailVerificationConfirmView.as_view(),
        name="email-verify",
    ),
    path(
        "email/resend/",
        ResendEmailVerificationView.as_view(),
        name="email-resend",
    ),
    path("me/", MeView.as_view(), name="me"),
    path("addresses/", AddressListCreateView.as_view(), name="address-list"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
]
