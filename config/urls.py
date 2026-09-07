from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path

from core.sitemaps import StaticViewSitemap


def google_verification(request):
    return HttpResponse(
        "google-site-verification: google00085f02df9fb9ff.html",
        content_type="text/html",
    )


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: https://dance-academy-jwmz.onrender.com/sitemap.xml\n",
        content_type="text/plain",
    )


urlpatterns = [
    path("admin/", admin.site.urls),

    # =====================================================
    # GOOGLE SEARCH CONSOLE VERIFICATION
    # =====================================================

    path(
        "google00085f02df9fb9ff.html",
        google_verification,
        name="google_verification",
    ),

    # =====================================================
    # SEARCH ENGINE CRAWLING
    # =====================================================

    path(
        "robots.txt",
        robots_txt,
        name="robots_txt",
    ),

    # =====================================================
    # XML SITEMAP
    # =====================================================

    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "static": StaticViewSitemap,
            }
        },
        name="sitemap",
    ),

    # =====================================================
    # CORE APPLICATION
    # =====================================================

    path(
        "",
        include("core.urls"),
    ),
]


# =========================================================
# LOCAL MEDIA SERVING
# =========================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )