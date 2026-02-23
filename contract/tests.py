"""Tests for contracts_backend contract app."""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from account.models import CustomUser
from contract.models import Contract


pytestmark = pytest.mark.django_db


# ── Helpers ─────────────────────────────────────────────────────────────────


def make_staff_user(email="staff@test.com", password="securepass123"):
    """Create a staff (can_create / can_update / can_delete / can_print) user."""
    user = CustomUser.objects.create_user(
        email=email,
        password=password,
        is_staff=True,
        can_create=True,
        can_update=True,
        can_delete=True,
        can_print=True,
    )
    token = str(AccessToken.for_user(user))
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return user, client


def make_readonly_user(email="readonly@test.com", password="securepass123"):
    """Create a user with no write permissions."""
    user = CustomUser.objects.create_user(
        email=email,
        password=password,
        is_staff=False,
        can_create=False,
        can_update=False,
        can_delete=False,
        can_print=False,
    )
    token = str(AccessToken.for_user(user))
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return user, client


def make_contract(created_by=None, numero="0001/26", **kwargs):
    """Create a minimal valid Contract instance."""
    defaults = {
        "numero_contrat": numero,
        "date_contrat": "2026-01-15",
        "statut": "Brouillon",
        "montant_ht": "50000.00",
        "tva": "20.00",
    }
    defaults.update(kwargs)
    if created_by is not None:
        defaults["created_by_user"] = created_by
    return Contract.objects.create(**defaults)


# ── Contract model ───────────────────────────────────────────────────────────


class TestContractModel:
    def test_str_returns_numero_contrat(self):
        user, _ = make_staff_user()
        contract = make_contract(created_by=user, numero="STR/01")
        assert str(contract) == "STR/01"

    def test_montant_tva_property(self):
        user, _ = make_staff_user()
        contract = make_contract(created_by=user, numero="TVA/01", montant_ht="10000.00", tva="20.00")
        assert contract.montant_tva == pytest.approx(2000.0)

    def test_montant_ttc_property(self):
        user, _ = make_staff_user()
        contract = make_contract(created_by=user, numero="TTC/01", montant_ht="10000.00", tva="20.00")
        assert contract.montant_ttc == pytest.approx(12000.0)

    def test_default_statut_is_brouillon(self):
        user, _ = make_staff_user()
        contract = Contract.objects.create(
            numero_contrat="DEF/01",
            date_contrat="2026-01-01",
            created_by_user=user,
        )
        assert contract.statut == "Brouillon"

    def test_default_confidentialite(self):
        user, _ = make_staff_user()
        contract = make_contract(created_by=user, numero="CONF/01")
        assert contract.confidentialite == "CONFIDENTIEL"

    def test_numero_contrat_unique(self):
        from django.db import IntegrityError

        user, _ = make_staff_user()
        make_contract(created_by=user, numero="UNIQ/01")
        with pytest.raises(IntegrityError):
            make_contract(created_by=user, numero="UNIQ/01")

    def test_created_by_user_nullable(self):
        contract = make_contract(numero="NULL/01")
        assert contract.created_by_user is None


# ── ContractListCreateView ───────────────────────────────────────────────────


class TestContractListCreateView:
    def setup_method(self):
        self.url = reverse("contract:contract-list-create")
        self.staff_user, self.staff_client = make_staff_user()
        self.readonly_user, self.readonly_client = make_readonly_user()
        self.anon_client = APIClient()

    def test_list_contracts_returns_200(self):
        make_contract(created_by=self.staff_user, numero="LIST/01")
        make_contract(created_by=self.staff_user, numero="LIST/02")
        response = self.staff_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_list_contracts_paginated(self):
        for i in range(3):
            make_contract(created_by=self.staff_user, numero=f"PAG/{i:02d}")
        response = self.staff_client.get(self.url, {"pagination": "true", "page": 1})
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data

    def test_list_contracts_unauthenticated_returns_401(self):
        response = self.anon_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_contract_as_staff_returns_201(self):
        payload = {
            "numero_contrat": "NEW/01",
            "date_contrat": "2026-03-01",
            "statut": "Brouillon",
            "montant_ht": "20000.00",
            "tva": "20.00",
        }
        response = self.staff_client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["numero_contrat"] == "NEW/01"

    def test_create_contract_without_can_create_returns_403(self):
        payload = {
            "numero_contrat": "NOPERM/01",
            "date_contrat": "2026-03-01",
            "statut": "Brouillon",
        }
        response = self.readonly_client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_contract_unauthenticated_returns_401(self):
        payload = {
            "numero_contrat": "ANON/01",
            "date_contrat": "2026-03-01",
        }
        response = self.anon_client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_contract_missing_required_field_returns_400(self):
        # numero_contrat is required
        payload = {"date_contrat": "2026-03-01", "statut": "Brouillon"}
        response = self.staff_client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_contracts_filter_by_statut(self):
        make_contract(created_by=self.staff_user, numero="FLT/01", statut="Signé")
        make_contract(created_by=self.staff_user, numero="FLT/02", statut="Brouillon")
        response = self.staff_client.get(self.url, {"statut": "Signé"})
        assert response.status_code == status.HTTP_200_OK
        for item in response.data:
            assert item["statut"] == "Signé"


# ── ContractDetailEditDeleteView ─────────────────────────────────────────────


class TestContractDetailEditDeleteView:
    def setup_method(self):
        self.staff_user, self.staff_client = make_staff_user()
        self.readonly_user, self.readonly_client = make_readonly_user(email="ro2@test.com")
        self.contract = make_contract(created_by=self.staff_user, numero="DET/01")
        self.url = reverse("contract:contract-detail", kwargs={"pk": self.contract.pk})
        self.anon_client = APIClient()

    def test_get_contract_returns_200(self):
        response = self.staff_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["numero_contrat"] == "DET/01"

    def test_get_contract_not_found_returns_404(self):
        url = reverse("contract:contract-detail", kwargs={"pk": 99999})
        response = self.staff_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_contract_unauthenticated_returns_401(self):
        response = self.anon_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_contract_as_staff_returns_200(self):
        payload = {
            "numero_contrat": "DET/01",
            "date_contrat": "2026-06-01",
            "statut": "Envoyé",
            "montant_ht": "60000.00",
            "tva": "20.00",
        }
        response = self.staff_client.put(self.url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["statut"] == "Envoyé"

    def test_put_contract_without_can_update_returns_403(self):
        payload = {
            "numero_contrat": "DET/01",
            "date_contrat": "2026-06-01",
            "statut": "Envoyé",
        }
        response = self.readonly_client.put(self.url, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_contract_as_staff_returns_204(self):
        contract = make_contract(created_by=self.staff_user, numero="DEL/01")
        url = reverse("contract:contract-detail", kwargs={"pk": contract.pk})
        response = self.staff_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Contract.objects.filter(pk=contract.pk).exists()

    def test_delete_contract_without_can_delete_returns_403(self):
        response = self.readonly_client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_contract_not_found_returns_404(self):
        url = reverse("contract:contract-detail", kwargs={"pk": 99999})
        response = self.staff_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ── ContractStatusUpdateView ─────────────────────────────────────────────────


class TestContractStatusUpdateView:
    def setup_method(self):
        self.staff_user, self.staff_client = make_staff_user()
        self.readonly_user, self.readonly_client = make_readonly_user(email="ro3@test.com")
        self.contract = make_contract(created_by=self.staff_user, numero="STAT/01", statut="Brouillon")
        self.url = reverse("contract:contract-statut-update", kwargs={"pk": self.contract.pk})

    def test_patch_statut_valid_returns_200(self):
        response = self.staff_client.patch(self.url, {"statut": "Envoyé"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["statut"] == "Envoyé"
        self.contract.refresh_from_db()
        assert self.contract.statut == "Envoyé"

    def test_patch_statut_invalid_returns_400(self):
        response = self.staff_client.patch(self.url, {"statut": "Inexistant"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_statut_without_can_update_returns_403(self):
        response = self.readonly_client.patch(self.url, {"statut": "Signé"}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_statut_not_found_returns_404(self):
        url = reverse("contract:contract-statut-update", kwargs={"pk": 99999})
        response = self.staff_client.patch(url, {"statut": "Signé"}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ── BulkDeleteContractView ───────────────────────────────────────────────────


class TestBulkDeleteContractView:
    def setup_method(self):
        self.staff_user, self.staff_client = make_staff_user()
        self.readonly_user, self.readonly_client = make_readonly_user(email="ro4@test.com")
        self.url = reverse("contract:contract-bulk-delete")

    def test_bulk_delete_valid_ids_returns_204(self):
        c1 = make_contract(created_by=self.staff_user, numero="BULK/01")
        c2 = make_contract(created_by=self.staff_user, numero="BULK/02")
        response = self.staff_client.delete(
            self.url, {"ids": [c1.pk, c2.pk]}, format="json"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Contract.objects.filter(pk__in=[c1.pk, c2.pk]).exists()

    def test_bulk_delete_missing_ids_returns_400(self):
        response = self.staff_client.delete(self.url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_delete_non_list_ids_returns_400(self):
        response = self.staff_client.delete(self.url, {"ids": "not-a-list"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_delete_invalid_integer_ids_returns_400(self):
        response = self.staff_client.delete(self.url, {"ids": ["abc", "xyz"]}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_delete_nonexistent_ids_returns_404(self):
        response = self.staff_client.delete(self.url, {"ids": [99998, 99999]}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_bulk_delete_without_can_delete_returns_403(self):
        c = make_contract(created_by=self.staff_user, numero="BULKPERM/01")
        response = self.readonly_client.delete(self.url, {"ids": [c.pk]}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── GenerateNumeroContratView ────────────────────────────────────────────────


class TestGenerateNumeroContratView:
    def setup_method(self):
        _, self.auth_client = make_staff_user()
        self.anon_client = APIClient()
        self.url = reverse("contract:generate-numero-contrat")

    def test_generate_returns_200_with_numero(self):
        response = self.auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert "numero_contrat" in response.data

    def test_generate_unauthenticated_returns_401(self):
        response = self.anon_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
