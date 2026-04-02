from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import COMPANY_CHOICES


class CompanyConfig(models.Model):
    """Global company identity details (EP / Entrepreneur Principal)."""

    company = models.CharField(
        max_length=50,
        choices=COMPANY_CHOICES,
        unique=True,
        verbose_name=_("Société"),
    )
    name = models.CharField(max_length=200, verbose_name=_("Raison sociale"))
    forme_juridique = models.CharField(
        max_length=50, blank=True, default="", verbose_name=_("Forme juridique")
    )
    capital = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Capital (DH)"),
    )
    rc = models.CharField(
        max_length=100, blank=True, default="", verbose_name=_("Registre de Commerce")
    )
    ice = models.CharField(max_length=100, blank=True, default="", verbose_name=_("ICE"))
    identifiant_fiscal = models.CharField(
        max_length=100, blank=True, default="", verbose_name=_("Identifiant Fiscal (IF)")
    )
    adresse = models.TextField(
        blank=True, default="", verbose_name=_("Adresse du siège social")
    )
    representant = models.CharField(
        max_length=200, blank=True, default="", verbose_name=_("Représentant légal")
    )
    qualite_representant = models.CharField(
        max_length=100, default=_("Gérant"), verbose_name=_("Qualité du représentant")
    )

    class Meta:
        verbose_name = _("Configuration Société")
        verbose_name_plural = _("Configurations Sociétés")

    def __str__(self) -> str:
        return f"{self.name} ({self.get_company_display()})"
