from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from .models import CompanyConfig


@admin.register(CompanyConfig)
class CompanyConfigAdmin(admin.ModelAdmin):
    list_display = ("company", "name", "forme_juridique", "representant")
    list_filter = ("company",)
    search_fields = ("name", "representant", "rc", "ice")


for model in (Group, Site):
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass
