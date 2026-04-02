from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContractConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "contract"
    verbose_name = _("Contrats")
