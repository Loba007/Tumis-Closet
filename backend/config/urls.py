from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import health, sitemap

urlpatterns = [
    path("health/", health, name="health"),
    path("sitemap.xml", sitemap, name="sitemap"),
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/categories/", include("categories.urls")),
    path("api/products/", include("products.urls")),
    path("api/cart/", include("cart.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/wishlist/", include("wishlist.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/contact/", include("contact.urls")),
]

if settings.DEBUG or settings.ALLOW_LOCAL_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
