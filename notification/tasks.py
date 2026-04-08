"""Celery tasks for contracts notification checks."""

import logging
from datetime import date, timedelta

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _

from notification.models import Notification, NotificationPreference

logger = logging.getLogger(__name__)


@shared_task(name="notification.check_contract_notifications")
def check_contract_notifications():
    """
    Periodic task that checks for critical contract time-sensitive events
    and creates notifications for all staff users. Runs every hour.

    Events checked:
    - Contracts sent (Envoyé) but not signed after unsigned_alert_days
    - Contracts where work start (date_debut) is approaching within work_start_alert_days
    - Contracts completed (Terminé) where reserve submission deadline is near
    """
    from contract.models import Contract

    today = timezone.now().date()
    channel_layer = get_channel_layer()

    # Notify all users who have preferences (staff see all contracts)
    preferences = NotificationPreference.objects.select_related("user").all()

    for pref in preferences:
        user = pref.user

        # Determine which contracts this user can see
        if user.is_staff:
            contracts_qs = Contract.objects.all()
        else:
            contracts_qs = Contract.objects.none()

        # ── Unsigned contracts ────────────────────────────────────────────
        if pref.notify_unsigned_contract:
            threshold = today - timedelta(days=pref.unsigned_alert_days)
            unsigned = contracts_qs.filter(
                statut="Envoyé",
                date_contrat__lte=threshold,
            )
            for contract in unsigned:
                exists = Notification.objects.filter(
                    user=user,
                    notification_type="unsigned_contract",
                    object_id=contract.id,
                ).exists()
                if not exists:
                    days_since = (today - contract.date_contrat).days
                    notif = Notification.objects.create(
                        user=user,
                        title=_("Contrat non signé — %(ref)s")
                        % {"ref": contract.numero_contrat},
                        message=_(
                            "Le contrat %(ref)s (%(client)s) a été envoyé il y a "
                            "%(days)s jours sans signature."
                        )
                        % {
                            "ref": contract.numero_contrat,
                            "client": contract.client_nom or "—",
                            "days": days_since,
                        },
                        notification_type="unsigned_contract",
                        object_id=contract.id,
                    )
                    _broadcast(channel_layer, user.id, notif)

        # ── Work start approaching ────────────────────────────────────────
        if pref.notify_work_start:
            alert_from = today
            alert_to = today + timedelta(days=pref.work_start_alert_days)
            starting_contracts = contracts_qs.filter(
                statut__in=["Signé", "En cours"],
                date_debut__gte=alert_from,
                date_debut__lte=alert_to,
            )
            for contract in starting_contracts:
                # Only alert for contracts starting in the future (not already started)
                if contract.date_debut and contract.date_debut >= today:
                    key = f"work_start_{contract.id}_{contract.date_debut}"
                    exists = Notification.objects.filter(
                        user=user,
                        notification_type="work_start",
                        object_id=contract.id,
                    ).exists()
                    if not exists:
                        days_until = (contract.date_debut - today).days
                        notif = Notification.objects.create(
                            user=user,
                            title=_("Début des travaux dans %(days)s jour(s) — %(ref)s")
                            % {"days": days_until, "ref": contract.numero_contrat},
                            message=_(
                                "Les travaux du contrat %(ref)s (%(client)s) débutent "
                                "le %(date)s."
                            )
                            % {
                                "ref": contract.numero_contrat,
                                "client": contract.client_nom or "—",
                                "date": contract.date_debut,
                            },
                            notification_type="work_start",
                            object_id=contract.id,
                        )
                        _broadcast(channel_layer, user.id, notif)

        # ── Reserve submission deadline ───────────────────────────────────
        if pref.notify_reserve_deadline:
            # For terminated contracts, check if reserve deadline is within 2 days
            terminated = contracts_qs.filter(statut="Terminé")
            for contract in terminated:
                reserve_days = getattr(contract, "delai_reserves", None) or 7
                # Use date_updated as proxy for when it became Terminé
                # (since there is no separate completion_date field)
                completion_date = (
                    contract.date_updated.date() if contract.date_updated else None
                )
                if not completion_date:
                    continue
                deadline = completion_date + timedelta(days=reserve_days)
                days_remaining = (deadline - today).days
                if 0 <= days_remaining <= 2:
                    key_type = "reserve_deadline"
                    exists = Notification.objects.filter(
                        user=user,
                        notification_type=key_type,
                        object_id=contract.id,
                    ).exists()
                    if not exists:
                        notif = Notification.objects.create(
                            user=user,
                            title=_("Délai réserves expire bientôt — %(ref)s")
                            % {"ref": contract.numero_contrat},
                            message=_(
                                "Le délai de dépôt des réserves pour le contrat %(ref)s "
                                "(%(client)s) expire le %(deadline)s (%(days)s jour(s) restant(s))."
                            )
                            % {
                                "ref": contract.numero_contrat,
                                "client": contract.client_nom or "—",
                                "deadline": deadline,
                                "days": days_remaining,
                            },
                            notification_type=key_type,
                            object_id=contract.id,
                        )
                        _broadcast(channel_layer, user.id, notif)


def notify_contract_status_change(contract, old_statut, new_statut):
    """
    Called from the contract view when status is changed.
    Creates a real-time notification for all staff users.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    channel_layer = get_channel_layer()
    staff_users = User.objects.filter(is_staff=True)

    for user in staff_users:
        pref, _created = NotificationPreference.objects.get_or_create(user=user)
        if not pref.notify_status_change:
            continue
        notif = Notification.objects.create(
            user=user,
            title=_("Statut mis à jour — %(ref)s") % {"ref": contract.numero_contrat},
            message=_(
                "Le statut du contrat %(ref)s (%(client)s) est passé de "
                "« %(old)s » à « %(new)s »."
            )
            % {
                "ref": contract.numero_contrat,
                "client": contract.client_nom or "—",
                "old": old_statut,
                "new": new_statut,
            },
            notification_type="status_change",
            object_id=contract.id,
        )
        _broadcast(channel_layer, user.id, notif)


def _broadcast(channel_layer, user_id, notification):
    """Send a notification event to the user's personal WS group."""
    try:
        async_to_sync(channel_layer.group_send)(
            str(user_id),
            {
                "type": "receive_group_message",
                "message": {
                    "type": "NOTIFICATION",
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "object_id": notification.object_id,
                    "is_read": notification.is_read,
                    "date_created": notification.date_created.isoformat(),
                },
            },
        )
    except Exception:
        logger.exception(
            "Failed to broadcast notification %s to user %s", notification.id, user_id
        )
