from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path


def google_verification(request):
    return HttpResponse(
        "google-site-verification: google00085f02df9fb9ff.html",
        content_type="text/html",
    )


urlpatterns = [
    path("admin/", admin.site.urls),

    # Google Search Console verification
    path(
        "google00085f02df9fb9ff.html",
        google_verification,
        name="google_verification",
    ),

    path("", include("core.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )