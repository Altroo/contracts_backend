from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from .models import CompanyConfig


@admin.register(CompanyConfig)
class CompanyConfigAdmin(SimpleHistoryAdmin):
    list_display = ("company", "name", "forme_juridique", "representant")
    list_filter = ("company",)
    search_fields = ("name", "representant", "rc", "ice")


class HistoricalCompanyConfigAdmin(admin.ModelAdmin):
    """Read-only admin for viewing historical CompanyConfig records."""

    list_display = (
        "history_id",
        "id",
        "company",
        "name",
        "representant",
        "history_type",
        "history_date",
        "history_user",
    )
    list_filter = ("history_type", "history_date", "company")
    search_fields = ("name", "representant", "rc", "ice")
    readonly_fields = [
        field.name
        for field in CompanyConfig._meta.get_fields()
        if hasattr(field, "name") and not field.many_to_many and not field.one_to_many
    ] + [
        "history_id",
        "history_date",
        "history_change_reason",
        "history_type",
        "history_user",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(CompanyConfig.history.model, HistoricalCompanyConfigAdmin)


for model in (Group, Site):
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass
