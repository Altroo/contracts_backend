from django.db import models

from core.constants import COMPANY_CHOICES


class CompanyConfig(models.Model):
    """Global company identity details (EP / Entrepreneur Principal)."""

    company = models.CharField(
        max_length=50,
        choices=COMPANY_CHOICES,
        unique=True,
        verbose_name="Société",
    )
    name = models.CharField(max_length=200, verbose_name="Raison sociale")
    forme_juridique = models.CharField(
        max_length=50, blank=True, default="", verbose_name="Forme juridique"
    )
    capital = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Capital (DH)",
    )
    rc = models.CharField(
        max_length=100, blank=True, default="", verbose_name="Registre de Commerce"
    )
    ice = models.CharField(max_length=100, blank=True, default="", verbose_name="ICE")
    identifiant_fiscal = models.CharField(
        max_length=100, blank=True, default="", verbose_name="Identifiant Fiscal (IF)"
    )
    adresse = models.TextField(
        blank=True, default="", verbose_name="Adresse du siège social"
    )
    representant = models.CharField(
        max_length=200, blank=True, default="", verbose_name="Représentant légal"
    )
    qualite_representant = models.CharField(
        max_length=100, default="Gérant", verbose_name="Qualité du représentant"
    )

    class Meta:
        verbose_name = "Configuration Société"
        verbose_name_plural = "Configurations Sociétés"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_company_display()})"
