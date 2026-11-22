"""
Django settings for Tunmis Closet (config project).
"""

import logging
from datetime import timedelta
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse

from decouple import Csv
from decouple import config as env
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------------
DEFAULT_SECRET_KEY = "django-insecure-change-me-in-production"
INSECURE_SECRET_MARKERS = (
    "change-this",
    "change-me",
    "insecure",
    "replace-with",
    "placeholder",
)
SECRET_KEY = env("SECRET_KEY", default=DEFAULT_SECRET_KEY)
DEBUG = env("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

PRODUCTION_FRONTEND_ORIGIN = "https://www.tunmiscloset.com"
LOCAL_FRONTEND_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"

# Render injects the public hostname at runtime. Keep it allow-listed
# automatically so a fresh deploy works without hard-coding the hostname.
RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default="").strip()
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

ADMIN_URL = env("ADMIN_URL", default="admin/").strip().lstrip("/")
if not ADMIN_URL.endswith("/"):
    ADMIN_URL = f"{ADMIN_URL}/"

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "cloudinary_storage",
    "cloudinary",

    # local apps
    "accounts",
    "categories",
    "products",
    "cart",
    "orders",
    "payments",
    "wishlist",
    "reviews",
    "contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# Defaults to SQLite for zero-config local dev. Set DATABASE_URL to point at
# Postgres, e.g. postgres://user:password@localhost:5432/tunmis_closet
# ---------------------------------------------------------------------------
import dj_database_url  # noqa: E402

DATABASE_URL = env("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# I18N
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudinary is used for product/portfolio images in production. Until real
# credentials are supplied, media falls back to local disk storage so the
# project runs out of the box.
USE_CLOUDINARY = env("USE_CLOUDINARY", default=False, cast=bool)
ALLOW_LOCAL_MEDIA = env("ALLOW_LOCAL_MEDIA", default=False, cast=bool)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": env("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": env("CLOUDINARY_API_SECRET", default=""),
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

if USE_CLOUDINARY:
    STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}

if not DEBUG:
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "config.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/min",
        "user": "300/min",
        "login": "5/min",
        "register": "10/min",
        "password-reset": "5/min",
        "email-verification": "5/min",
        "contact": "5/min",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# CORS — allow the Vite dev server / deployed frontend
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in env(
        "CORS_ALLOWED_ORIGINS",
        default=LOCAL_FRONTEND_ORIGINS if DEBUG else PRODUCTION_FRONTEND_ORIGIN,
        cast=Csv(),
    )
    if origin.strip()
]
CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)
CORS_ALLOW_CREDENTIALS = env("CORS_ALLOW_CREDENTIALS", default=False, cast=bool)
CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in env(
        "CSRF_TRUSTED_ORIGINS",
        default=LOCAL_FRONTEND_ORIGINS if DEBUG else PRODUCTION_FRONTEND_ORIGIN,
        cast=Csv(),
    )
    if origin.strip()
]

# ---------------------------------------------------------------------------
# Email / contact notifications
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.console.EmailBackend"
        if DEBUG
        else "django.core.mail.backends.smtp.EmailBackend"
    ),
)
EMAIL_HOST = env("EMAIL_HOST", default="" if DEBUG else "smtp-relay.brevo.com")
EMAIL_PORT = env("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_TIMEOUT = env("EMAIL_TIMEOUT", default=15, cast=int)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@tunmiscloset.com")
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
CONTACT_EMAIL = env("CONTACT_EMAIL", default="" if DEBUG else "hello@tunmiscloset.com")
ALLOW_CONSOLE_EMAIL = env("ALLOW_CONSOLE_EMAIL", default=False, cast=bool)
REQUIRE_EMAIL_VERIFICATION = env(
    "REQUIRE_EMAIL_VERIFICATION", default=not DEBUG, cast=bool
)
PASSWORD_RESET_TIMEOUT = env("PASSWORD_RESET_TIMEOUT", default=3600, cast=int)
EMAIL_VERIFICATION_TIMEOUT = env(
    "EMAIL_VERIFICATION_TIMEOUT", default=60 * 60 * 24 * 3, cast=int
)

# ---------------------------------------------------------------------------
# Paystack (payments app)
# ---------------------------------------------------------------------------
PAYSTACK_SECRET_KEY = env("PAYSTACK_SECRET_KEY", default="")
PAYSTACK_PUBLIC_KEY = env("PAYSTACK_PUBLIC_KEY", default="")
PAYMENTS_ENABLED = bool(PAYSTACK_SECRET_KEY and PAYSTACK_PUBLIC_KEY)
PAYSTACK_MODE = env("PAYSTACK_MODE", default="test").strip().lower()
ALLOW_TEST_PAYMENTS = env("ALLOW_TEST_PAYMENTS", default=False, cast=bool)
PAYSTACK_BASE_URL = "https://api.paystack.co"

# Frontend base URL, used to build payment/email callback links
FRONTEND_URL = env(
    "FRONTEND_URL",
    default="http://localhost:5173" if DEBUG else PRODUCTION_FRONTEND_ORIGIN,
).rstrip("/")

# ---------------------------------------------------------------------------
# Production security
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
# Health checks hit the container/host directly over HTTP; redirecting them
# to HTTPS makes Render/Railway/Docker health probes fail.
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", default=not DEBUG, cast=bool)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", default=0 if DEBUG else 31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Optional error tracking (Sentry). Disabled unless SENTRY_DSN is set.
# ---------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_ENVIRONMENT = env(
    "SENTRY_ENVIRONMENT", default="development" if DEBUG else "production"
)
SENTRY_TRACES_SAMPLE_RATE = env("SENTRY_TRACES_SAMPLE_RATE", default=0.0, cast=float)

if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
    except ImportError:  # pragma: no cover - optional dependency
        logging.getLogger(__name__).warning(
            "SENTRY_DSN is set but sentry-sdk is not installed; error tracking disabled."
        )
    else:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=SENTRY_ENVIRONMENT,
            integrations=[DjangoIntegration()],
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
            send_default_pii=False,
        )

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "payments": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "orders": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}


def _is_local_host(host):
    host = (host or "").strip().lower()
    if host.startswith("["):
        host = host[1:].split("]", 1)[0]
    elif host.count(":") == 1:
        host = host.split(":", 1)[0]

    try:
        address = ip_address(host)
    except ValueError:
        return host == "localhost" or host.endswith(".localhost")
    return address.is_loopback or address.is_unspecified


def _is_local_url(url):
    parsed = urlparse(url or "")
    return _is_local_host(parsed.hostname or "")


def _validate_production_settings():
    """Fail fast on unsafe config; warn when optional integrations are unconfigured."""
    if DEBUG:
        return

    errors = []
    warnings = []

    secret = SECRET_KEY or ""
    if len(secret) < 50 or secret == DEFAULT_SECRET_KEY:
        errors.append("SECRET_KEY must be a unique value of at least 50 characters.")
    if any(marker in secret.lower() for marker in INSECURE_SECRET_MARKERS):
        errors.append("SECRET_KEY still contains an insecure placeholder value.")

    if not DATABASE_URL:
        errors.append("DATABASE_URL is required when DEBUG=False.")
    elif DATABASE_URL.lower().startswith("sqlite"):
        errors.append("Use PostgreSQL (not SQLite) when DEBUG=False.")

    if "*" in ALLOWED_HOSTS:
        errors.append("ALLOWED_HOSTS must not contain the wildcard '*'.")
    if not any(not _is_local_host(host) for host in ALLOWED_HOSTS):
        errors.append("ALLOWED_HOSTS must include the public API hostname.")

    frontend = urlparse(FRONTEND_URL)
    if (
        frontend.scheme != "https"
        or _is_local_url(FRONTEND_URL)
        or not frontend.netloc
        or frontend.path not in ("", "/")
        or frontend.query
        or frontend.fragment
        or frontend.username
        or frontend.password
    ):
        errors.append("FRONTEND_URL must be the public HTTPS frontend URL.")

    frontend_origin = f"{frontend.scheme}://{frontend.netloc}"
    if not any(origin.rstrip("/") == frontend_origin for origin in CORS_ALLOWED_ORIGINS):
        errors.append("CORS_ALLOWED_ORIGINS must include FRONTEND_URL's exact origin.")
    if not any(origin.rstrip("/") == frontend_origin for origin in CSRF_TRUSTED_ORIGINS):
        errors.append("CSRF_TRUSTED_ORIGINS must include FRONTEND_URL's exact origin.")
    if any(
        _is_local_url(origin) or urlparse(origin).scheme != "https"
        for origin in CORS_ALLOWED_ORIGINS
    ):
        errors.append("Production CORS origins must use HTTPS and must not include local origins.")
    if any(
        _is_local_url(origin) or urlparse(origin).scheme != "https"
        for origin in CSRF_TRUSTED_ORIGINS
    ):
        errors.append("Production CSRF trusted origins must use HTTPS and must not include local origins.")
    if CORS_ALLOW_ALL_ORIGINS:
        errors.append("CORS_ALLOW_ALL_ORIGINS must be disabled when DEBUG=False.")

    if PAYSTACK_MODE not in {"test", "live"}:
        errors.append("PAYSTACK_MODE must be either 'test' or 'live'.")
    if not (PAYSTACK_SECRET_KEY and PAYSTACK_PUBLIC_KEY):
        warnings.append(
            "Paystack credentials are not configured; payment endpoints are disabled."
        )
    else:
        if len(PAYSTACK_SECRET_KEY) < 20:
            errors.append("PAYSTACK_SECRET_KEY must be a real key.")
        if len(PAYSTACK_PUBLIC_KEY) < 20:
            errors.append("PAYSTACK_PUBLIC_KEY must be a real key.")
        secret_prefix = "sk_live_" if PAYSTACK_MODE == "live" else "sk_test_"
        public_prefix = "pk_live_" if PAYSTACK_MODE == "live" else "pk_test_"
        if not PAYSTACK_SECRET_KEY.startswith(secret_prefix):
            errors.append(f"PAYSTACK_SECRET_KEY must use the {PAYSTACK_MODE} key prefix.")
        if not PAYSTACK_PUBLIC_KEY.startswith(public_prefix):
            errors.append(f"PAYSTACK_PUBLIC_KEY must use the {PAYSTACK_MODE} key prefix.")
        if PAYSTACK_MODE == "test" and not ALLOW_TEST_PAYMENTS:
            errors.append(
                "Test Paystack keys are blocked when DEBUG=False. "
                "Set ALLOW_TEST_PAYMENTS=True only for an explicitly non-customer-facing environment."
            )

    if not USE_CLOUDINARY and not ALLOW_LOCAL_MEDIA:
        warnings.append(
            "Media uses local storage; uploads will not persist on an ephemeral host. "
            "Set USE_CLOUDINARY=True with Cloudinary credentials for production."
        )
    if USE_CLOUDINARY and not all(
        CLOUDINARY_STORAGE[key] for key in ("CLOUD_NAME", "API_KEY", "API_SECRET")
    ):
        errors.append("Cloudinary requires CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET.")

    if (
        EMAIL_BACKEND.endswith("console.EmailBackend")
        and not ALLOW_CONSOLE_EMAIL
    ):
        errors.append(
            "Configure a real EMAIL_BACKEND (e.g. SMTP) when DEBUG=False."
        )
    if EMAIL_BACKEND.endswith("smtp.EmailBackend") and not EMAIL_HOST:
        errors.append("EMAIL_HOST is required when using Django's SMTP email backend.")
    if not CONTACT_EMAIL:
        errors.append("CONTACT_EMAIL is required for order and enquiry notifications.")
    if EMAIL_USE_TLS and EMAIL_USE_SSL:
        errors.append("EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be enabled.")
    if not SECURE_SSL_REDIRECT:
        errors.append("SECURE_SSL_REDIRECT must be enabled when DEBUG=False.")
    if not SESSION_COOKIE_SECURE or not CSRF_COOKIE_SECURE:
        errors.append("SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE must be enabled when DEBUG=False.")
    if SECURE_HSTS_SECONDS <= 0:
        errors.append("SECURE_HSTS_SECONDS must be greater than zero when DEBUG=False.")

    if warnings:
        logging.getLogger(__name__).warning(
            "Production configuration warnings:\n- " + "\n- ".join(warnings)
        )
    if errors:
        raise ImproperlyConfigured(
            "Production configuration problems:\n- " + "\n- ".join(errors)
        )


_validate_production_settings()
