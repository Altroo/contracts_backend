from django.urls import path

from .views import CompanyConfigListView

urlpatterns = [
    path("", CompanyConfigListView.as_view(), name="company-config-list"),
]
