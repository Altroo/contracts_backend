from rest_framework import serializers

from .models import CompanyConfig


class CompanyConfigSerializer(serializers.ModelSerializer):
    """Read-only serializer for company configuration."""

    company_display = serializers.CharField(
        source="get_company_display", read_only=True
    )

    class Meta:
        model = CompanyConfig
        fields = [
            "id",
            "company",
            "company_display",
            "name",
            "forme_juridique",
            "capital",
            "rc",
            "ice",
            "identifiant_fiscal",
            "adresse",
            "representant",
            "qualite_representant",
        ]
        read_only_fields = fields
