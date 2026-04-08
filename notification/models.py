from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from django.conf import settings


class NotificationPreference(models.Model):
    """User-specific notification preferences for contract events."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preference",
        verbose_name=_("Utilisateur"),
    )
    notify_unsigned_contract = models.BooleanField(
        default=True,
        verbose_name=_("Notifier les contrats envoyés non signés"),
    )
    notify_work_start = models.BooleanField(
        default=True,
        verbose_name=_("Notifier le début des travaux"),
    )
    notify_reserve_deadline = models.BooleanField(
        default=True,
        verbose_name=_("Notifier l'échéance des réserves"),
    )
    notify_status_change = models.BooleanField(
        default=True,
        verbose_name=_("Notifier les changements de statut"),
    )
    unsigned_alert_days = models.PositiveIntegerField(
        default=7,
        verbose_name=_("Alerter après X jours sans signature"),
    )
    work_start_alert_days = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Alerter X jours avant le début des travaux"),
    )
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Date création")
    )
    date_updated = models.DateTimeField(
        auto_now=True, verbose_name=_("Date modification")
    )
    history = HistoricalRecords(
        verbose_name=_("Historique Préférence Notification"),
        verbose_name_plural=_("Historiques Préférences Notifications"),
    )

    class Meta:
        verbose_name = _("Préférence de notification")
        verbose_name_plural = _("Préférences de notification")

    def __str__(self) -> str:
        return f"Notifications — {self.user.email}"


class Notification(models.Model):
    """A notification sent to a user about a contract event."""

    NOTIFICATION_TYPES = [
        ("unsigned_contract", _("Contrat non signé")),
        ("work_start", _("Début des travaux")),
        ("reserve_deadline", _("Échéance des réserves")),
        ("status_change", _("Changement de statut")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Utilisateur"),
    )
    title = models.CharField(max_length=255, verbose_name=_("Titre"))
    message = models.TextField(verbose_name=_("Message"))
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        verbose_name=_("Type"),
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("ID du contrat lié"),
    )
    is_read = models.BooleanField(default=False, verbose_name=_("Lu"))
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Date création"), db_index=True
    )
    history = HistoricalRecords(
        verbose_name=_("Historique Notification"),
        verbose_name_plural=_("Historiques Notifications"),
    )

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ("-date_created",)

    def __str__(self) -> str:
        return f"{self.title} — {self.user.email}"
