from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Protocol, TypedDict, TypeAlias

DateLike: TypeAlias = date | datetime | str | None
NumericLike: TypeAlias = Decimal | float | int | str | None


class PaymentTranche(TypedDict, total=False):
    label: str
    pourcentage: Decimal | float | int | str


class ArticleSection(TypedDict):
    num: str
    title: str
    body: str


class PlanCard(TypedDict):
    label: str
    val: str


class ContractDocumentLike(Protocol):
    id: int
    adresse_travaux: str | None
    annexes: str | None
    architecte: str | None
    clause_spec: str | None
    clauses_actives: list[str] | None
    client_adresse: str | None
    client_cin: str | None
    client_email: str | None
    client_nom: str | None
    client_qualite: str | None
    client_tel: str | None
    conditions_acces: str | None
    confidentialite: str | None
    date_contrat: DateLike
    date_debut: DateLike
    delai_reserves: NumericLike
    delai_retard: NumericLike
    description_travaux: str | None
    devise: str | None
    duree_estimee: str | None
    exclusions: str | None
    frais_redemarrage: NumericLike
    garantie: str | None
    mode_paiement_texte: str | None
    montant_ht: NumericLike
    numero_contrat: str | None
    penalite_retard: NumericLike
    penalite_retard_unite: str | None
    responsable_projet: str | None
    rib: str | None
    services: list[str] | None
    surface: NumericLike
    tranches: list[PaymentTranche] | None
    tribunal: str | None
    tva: NumericLike
    type_bien: str | None
    type_contrat: str | None
    ville_signature: str | None