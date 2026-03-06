import logging

from django.db import transaction
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from contracts_backend.utils import CustomPagination
from core.permissions import can_create, can_update, can_delete, can_print
from .filters import ContractFilter
from .models import Contract, Project
from .serializers import ContractListSerializer, ContractSerializer, ProjectSerializer
from .utils import get_next_numero_contrat
from .pdf import ContractPDFGenerator
from .doc import ContractDOCGenerator
from .bl_pdf import BluelinePDFGenerator
from .bl_doc import BluelineDOCGenerator
from .st_pdf import SousTraitancePDFGenerator
from .st_doc import SousTraitanceDOCGenerator

logger = logging.getLogger(__name__)


class ContractListCreateView(APIView):
    """GET paginated/full contract list and POST create a new contract."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        pagination = request.query_params.get("pagination", "false").lower() == "true"

        base_qs = (
            Contract.objects.all().select_related("created_by_user").order_by("-id")
        )
        filterset = ContractFilter(request.GET, queryset=base_qs)
        ordered_qs = filterset.qs

        if pagination:
            paginator = CustomPagination()
            page = paginator.paginate_queryset(ordered_qs, request)
            serializer = ContractListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ContractListSerializer(ordered_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request, *args, **kwargs):
        if not can_create(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour créer un contrat.")
            )

        serializer = ContractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(created_by_user=request.user)
        response_serializer = ContractSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ContractDetailEditDeleteView(APIView):
    """GET, PUT, DELETE a single contract by pk."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def _get_contract(pk: int) -> Contract:
        try:
            return Contract.objects.select_related("created_by_user").get(pk=pk)
        except Contract.DoesNotExist:
            raise Http404(_("Aucun contrat ne correspond à la requête."))

    def get(self, request, pk: int, *args, **kwargs):
        contract = self._get_contract(pk)
        serializer = ContractSerializer(contract)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk: int, *args, **kwargs):
        if not can_update(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour modifier ce contrat.")
            )
        contract = self._get_contract(pk)
        serializer = ContractSerializer(contract, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by_user=contract.created_by_user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        if not can_delete(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour supprimer ce contrat.")
            )
        contract = self._get_contract(pk)
        contract.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateNumeroContratView(APIView):
    """GET auto-generate the next contract reference."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        company = request.query_params.get("company", "")
        contract_category = request.query_params.get("contract_category", "")
        numero = get_next_numero_contrat(
            company=company, contract_category=contract_category
        )
        return Response({"numero_contrat": numero}, status=status.HTTP_200_OK)


class ContractStatusUpdateView(APIView):
    """PATCH the statut of a contract."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def _get_contract(pk: int) -> Contract:
        try:
            return Contract.objects.get(pk=pk)
        except Contract.DoesNotExist:
            raise Http404(_("Aucun contrat ne correspond à la requête."))

    def patch(self, request, pk: int, *args, **kwargs):
        if not can_update(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour modifier ce contrat.")
            )
        contract = self._get_contract(pk)
        new_status = request.data.get("statut")
        valid_statuses = [choice[0] for choice in contract.STATUT_CHOICES]
        if new_status not in valid_statuses:
            raise ValidationError({"statut": _("Statut invalide.")})
        contract.statut = new_status
        contract.save(update_fields=["statut"])
        return Response({"statut": contract.statut}, status=status.HTTP_200_OK)


class BulkDeleteContractView(APIView):
    """DELETE a list of contracts by their IDs."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def delete(request, *args, **kwargs):
        if not can_delete(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour supprimer des contrats.")
            )

        ids = request.data.get("ids")
        if not ids or not isinstance(ids, list):
            raise ValidationError({"ids": _("Une liste d'identifiants est requise.")})

        try:
            ids = [int(i) for i in ids]
        except (ValueError, TypeError):
            raise ValidationError(
                {"ids": _("Les identifiants doivent être des entiers.")}
            )

        contracts = list(Contract.objects.filter(pk__in=ids).only("id"))
        if len(contracts) != len(ids):
            raise Http404(_("Certains contrats sont introuvables."))

        with transaction.atomic():
            Contract.objects.filter(pk__in=ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ContractPDFView(APIView):
    """GET generate a PDF for a contract."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def _get_contract(pk: int) -> Contract:
        try:
            return Contract.objects.select_related("created_by_user").get(pk=pk)
        except Contract.DoesNotExist:
            raise Http404(_("Aucun contrat ne correspond à la requête."))

    def get(self, request, pk: int, language: str = "fr", *args, **kwargs):
        if not can_print(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour imprimer ce contrat.")
            )
        contract = self._get_contract(pk)
        if contract.company == "blueline_works":
            generator = BluelinePDFGenerator(contract, language=language)
        elif contract.contract_category == "sous_traitance":
            generator = SousTraitancePDFGenerator(contract, language=language)
        else:
            generator = ContractPDFGenerator(contract, language=language)
        return generator.generate_response()


class ContractDOCView(APIView):
    """GET generate a DOCX Word document for a contract."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def _get_contract(pk: int) -> Contract:
        try:
            return Contract.objects.select_related("created_by_user").get(pk=pk)
        except Contract.DoesNotExist:
            raise Http404(_("Aucun contrat ne correspond à la requête."))

    def get(self, request, pk: int, language: str = "fr", *args, **kwargs):
        if not can_print(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour télécharger ce contrat.")
            )
        contract = self._get_contract(pk)
        if contract.company == "blueline_works":
            generator = BluelineDOCGenerator(contract, language=language)
        elif contract.contract_category == "sous_traitance":
            generator = SousTraitanceDOCGenerator(contract, language=language)
        else:
            generator = ContractDOCGenerator(contract, language=language)
        return generator.generate_response()


# ── Project views ────────────────────────────────────────────────────────────


class ProjectListCreateView(APIView):
    """GET list all projects, POST create a new project."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        company = request.query_params.get("company", "")
        qs = Project.objects.all().order_by("name")
        if company:
            qs = qs.filter(company=company)
        serializer = ProjectSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request, *args, **kwargs):
        if not can_create(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour créer un projet.")
            )
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by_user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    """GET, PUT, DELETE a single project."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def _get_project(pk: int) -> Project:
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404(_("Aucun projet ne correspond à la requête."))

    def get(self, request, pk: int, *args, **kwargs):
        project = self._get_project(pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk: int, *args, **kwargs):
        if not can_update(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour modifier ce projet.")
            )
        project = self._get_project(pk)
        serializer = ProjectSerializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        if not can_delete(request.user):
            raise PermissionDenied(
                _("Vous n'avez pas les droits pour supprimer ce projet.")
            )
        project = self._get_project(pk)
        if project.is_predefined:
            raise PermissionDenied(
                _("Les projets prédéfinis ne peuvent pas être supprimés.")
            )
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
