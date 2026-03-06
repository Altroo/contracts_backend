from django.contrib import admin

from .models import CompanyConfig


@admin.register(CompanyConfig)
class CompanyConfigAdmin(admin.ModelAdmin):
    list_display = ("company", "name", "forme_juridique", "representant")
    list_filter = ("company",)
    search_fields = ("name", "representant", "rc", "ice")
