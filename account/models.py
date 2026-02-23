from io import BytesIO
from os import path
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from contracts_backend.settings import API_URL
from .managers import CustomUserManager


class Role(models.Model):
    """Custom role model."""

    name = models.CharField(max_length=150, unique=True, verbose_name="Nom rôle")
    name.help_text = "Nom unique du rôle"

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ("name",)

    def __str__(self):
        return self.name


def get_avatar_path(_, filename):
    _, ext = path.splitext(filename)
    return path.join("user_avatars/", str(uuid4()) + ext)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Adresse e‑mail", unique=True)
    first_name = models.CharField("Prénom", max_length=30, blank=True)
    last_name = models.CharField("Nom", max_length=30, blank=True)
    GENDER_CHOICES = (("", "Unset"), ("H", "Homme"), ("F", "Femme"))
    gender = models.CharField(
        verbose_name="Sexe",
        max_length=1,
        choices=GENDER_CHOICES,
        default="",
    )
    avatar = models.ImageField(
        verbose_name="Photo de profil",
        upload_to=get_avatar_path,
        blank=True,
        null=True,
        default=None,
    )
    avatar_cropped = models.ImageField(
        upload_to=get_avatar_path,
        blank=True,
        null=True,
        default=None,
        verbose_name="Photo de profil recadrée",
        max_length=1000,
    )
    is_staff = models.BooleanField(
        "Statut personnel",
        default=False,
        db_index=True,
    )
    is_active = models.BooleanField(
        "Actif",
        default=True,
        db_index=True,
    )
    date_joined = models.DateTimeField(
        "Date d'inscription",
        default=timezone.now,
        db_index=True,
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification",
        db_index=True,
    )
    password_reset_code = models.CharField(
        verbose_name="Mot de passe - Code de réinitialisation",
        blank=True,
        null=True,
        db_index=True,
    )
    password_reset_code_created_at = models.DateTimeField(
        verbose_name="Mot de passe - Date de création du code",
        blank=True,
        null=True,
        db_index=True,
    )
    task_id_password_reset = models.CharField(
        verbose_name="Mot de passe - Task ID de réinitialisation",
        max_length=40,
        default=None,
        null=True,
        blank=True,
        db_index=True,
    )
    default_password_set = models.BooleanField(
        verbose_name="Mot de passe par défaut défini",
        default=False,
        db_index=True,
    )
    # Per-user permission flags (staff users bypass these checks)
    can_view = models.BooleanField("Peut consulter", default=True)
    can_print = models.BooleanField("Peut imprimer", default=True)
    can_create = models.BooleanField("Peut créer", default=False)
    can_edit = models.BooleanField("Peut modifier", default=False)
    can_delete = models.BooleanField("Peut supprimer", default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    history = HistoricalRecords(
        verbose_name="Historique Utilisateur",
        verbose_name_plural="Historiques Utilisateurs"
    )

    def __str__(self):
        full_name = "{} {}".format(self.first_name, self.last_name).strip()
        return full_name if full_name else self.email

    @property
    def get_absolute_avatar_img(self):
        if self.avatar:
            return f"{API_URL}{self.avatar.url}"
        return None

    @property
    def get_absolute_avatar_cropped_img(self):
        if self.avatar_cropped:
            return f"{API_URL}{self.avatar_cropped.url}"
        return None

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ("-date_joined",)

    def save_image(self, file_name, image):
        if not isinstance(image, BytesIO):
            return
        getattr(self, file_name).save(
            f"{str(uuid4())}.webp", ContentFile(image.getvalue()), save=True
        )
