import django_filters
from django.db.models import Q

from .models import Contract


class ContractFilter(django_filters.FilterSet):
    """Filter for the Contract model."""

    search = django_filters.CharFilter(method="global_search", label="Recherche")
    statut = django_filters.CharFilter(method="filter_statut", label="Statut")
    type_contrat = django_filters.CharFilter(field_name="type_contrat", lookup_expr="exact")
    devise = django_filters.CharFilter(field_name="devise", lookup_expr="exact")
    date_after = django_filters.DateFilter(method="filter_date_after", label="Date après")
    date_before = django_filters.DateFilter(method="filter_date_before", label="Date avant")

    # Numeric range filters for montant_ht
    montant_ht = django_filters.NumberFilter(field_name="montant_ht", lookup_expr="exact")
    montant_ht__gt = django_filters.NumberFilter(field_name="montant_ht", lookup_expr="gt")
    montant_ht__gte = django_filters.NumberFilter(field_name="montant_ht", lookup_expr="gte")
    montant_ht__lt = django_filters.NumberFilter(field_name="montant_ht", lookup_expr="lt")
    montant_ht__lte = django_filters.NumberFilter(field_name="montant_ht", lookup_expr="lte")

    def global_search(self, queryset, name, value):  # noqa: ARG002
        return queryset.filter(
            Q(numero_contrat__icontains=value)
            | Q(client_nom__icontains=value)
            | Q(client_email__icontains=value)
            | Q(adresse_travaux__icontains=value)
            | Q(responsable_projet__icontains=value)
        )

    def filter_statut(self, queryset, name, value):  # noqa: ARG002
        statuts = [s.strip() for s in value.split(",") if s.strip()]
        if statuts:
            return queryset.filter(statut__in=statuts)
        return queryset

    def filter_date_after(self, queryset, name, value):  # noqa: ARG002
        return queryset.filter(date_contrat__gte=value)

    def filter_date_before(self, queryset, name, value):  # noqa: ARG002
        return queryset.filter(date_contrat__lte=value)

    class Meta:
        model = Contract
        fields = [
            "statut",
            "type_contrat",
            "devise",
            "date_after",
            "date_before",
            "montant_ht",
        ]
