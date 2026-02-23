from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "healthy"})


def custom_404(request, exception=None):
    return JsonResponse(
        {"status_code": 404, "message": "Page introuvable", "details": {}},
        status=404,
    )


def custom_500(request):
    return JsonResponse(
        {"status_code": 500, "message": "Erreur interne du serveur", "details": {}},
        status=500,
    )


handler404 = custom_404
handler500 = custom_500

urlpatterns = [
    path("api/health/", health_check, name="health-check"),
    path("api/account/", include("account.urls")),
    path("api/contract/", include("contract.urls")),
    path("gestion-interne-x7k2/", admin.site.urls),
]
