from xml.sax.saxutils import escape

from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from categories.models import Category
from products.models import Product

STATIC_PAGES = [
    ("", 1.0),
    ("shop", 0.9),
    ("portfolio", 0.8),
    ("about", 0.6),
    ("contact", 0.6),
    ("faq", 0.5),
    ("size-guide", 0.5),
    ("returns", 0.4),
    ("privacy", 0.3),
    ("terms", 0.3),
]


@require_GET
def health(request):
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "unhealthy"}, status=503)
    return JsonResponse({"status": "ok"})


@require_GET
@cache_page(60 * 15)
def sitemap(request):
    """Sitemap of storefront URLs, served from the API for Search Console."""
    base = settings.FRONTEND_URL.rstrip("/")

    entries = [f"<url><loc>{escape(f'{base}/{path}'.rstrip('/'))}</loc>"
               f"<priority>{priority:.1f}</priority></url>"
               for path, priority in STATIC_PAGES]

    for product in Product.objects.filter(is_active=True).only("slug", "updated_at"):
        lastmod = product.updated_at.strftime("%Y-%m-%d")
        entries.append(
            f"<url><loc>{escape(f'{base}/product/{product.slug}')}</loc>"
            f"<lastmod>{lastmod}</lastmod><priority>0.7</priority></url>"
        )

    for category in Category.objects.filter(is_active=True).only("slug"):
        entries.append(
            f"<url><loc>{escape(f'{base}/shop?category={category.slug}')}</loc>"
            f"<priority>0.6</priority></url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(entries)
        + "</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")
