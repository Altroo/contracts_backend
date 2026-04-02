import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Contract


class ContractFilter(django_filters.FilterSet):
    """Filter for the Contract model."""

    search = django_filters.CharFilter(method="global_search", label=_("Recherche"))
    statut = django_filters.CharFilter(method="filter_statut", label=_("Statut"))
    company = django_filters.CharFilter(method="filter_company", label=_("Société"))
    contract_category = django_filters.CharFilter(
        field_name="contract_category", lookup_expr="exact"
    )
    type_contrat = django_filters.CharFilter(
        field_name="type_contrat", lookup_expr="exact"
    )
    devise = django_filters.CharFilter(field_name="devise", lookup_expr="exact")
    date_after = django_filters.DateFilter(
        method="filter_date_after", label=_("Date après")
    )
    date_before = django_filters.DateFilter(
        method="filter_date_before", label=_("Date avant")
    )

    # Numeric range filters for montant_ht
    montant_ht = django_filters.NumberFilter(
        field_name="montant_ht", lookup_expr="exact"
    )
    montant_ht__gt = django_filters.NumberFilter(
        field_name="montant_ht", lookup_expr="gt"
    )
    montant_ht__gte = django_filters.NumberFilter(
        field_name="montant_ht", lookup_expr="gte"
    )
    montant_ht__lt = django_filters.NumberFilter(
        field_name="montant_ht", lookup_expr="lt"
    )
    montant_ht__lte = django_filters.NumberFilter(
        field_name="montant_ht", lookup_expr="lte"
    )

    def global_search(self, queryset, name, value):  # noqa: ARG002
        return queryset.filter(
            Q(numero_contrat__icontains=value)
            | Q(client_nom__icontains=value)
            | Q(client_email__icontains=value)
            | Q(adresse_travaux__icontains=value)
            | Q(responsable_projet__icontains=value)
            | Q(st_name__icontains=value)
            | Q(st_rep__icontains=value)
        )

    @staticmethod
    def filter_statut(queryset, name, value):  # noqa: ARG002
        statuts = [s.strip() for s in value.split(",") if s.strip()]
        if statuts:
            return queryset.filter(statut__in=statuts)
        return queryset

    @staticmethod
    def filter_company(queryset, name, value):  # noqa: ARG002
        companies = [c.strip() for c in value.split(",") if c.strip()]
        if companies:
            return queryset.filter(company__in=companies)
        return queryset

    @staticmethod
    def filter_date_after(queryset, name, value):  # noqa: ARG002
        return queryset.filter(date_contrat__gte=value)

    @staticmethod
    def filter_date_before(queryset, name, value):  # noqa: ARG002
        return queryset.filter(date_contrat__lte=value)

    class Meta:
        model = Contract
        fields = [
            "statut",
            "company",
            "contract_category",
            "type_contrat",
            "devise",
            "date_after",
            "date_before",
            "montant_ht",
        ]
