"""Bindings to existing Contracts operations. No new financial rules."""
from dataclasses import dataclass
from contract.models import Contract, Project
from contract.serializers import ContractSerializer, ProjectSerializer
from contract.views import ContractDetailEditDeleteView, ProjectDetailView
from contract.filters import ContractFilter
from account.models import CustomUser


@dataclass(frozen=True)
class Resource:
    model: object
    serializer: object = None
    view: object = None
    filterset: object = None
    editable: tuple = ()


RESOURCES = {
    "contract": Resource(Contract, ContractSerializer, ContractDetailEditDeleteView, ContractFilter,
        ("client_nom", "client_tel", "client_email", "adresse_travaux", "description_travaux", "date_debut", "duree_estimee", "notes", "st_lot_description", "st_observations")),
    "project": Resource(Project, ProjectSerializer, ProjectDetailView, None,
        ("name", "description", "adresse", "maitre_ouvrage", "permis")),
    "user": Resource(CustomUser),
}
