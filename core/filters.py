from datetime import datetime, time, timedelta

import django_filters
from django.conf import settings
from django.db.models import Q
from django.utils import timezone


class CalendarDateFilter(django_filters.DateFilter):
    """Compare a timestamp against complete local calendar days."""

    def filter(self, qs, value):
        if value is None:
            return qs
        # Use the next midnight exclusively for an upper bound. This includes
        # the whole final day and keeps the timestamp column's index usable.
        upper_bound = self.lookup_expr == "lte"
        day = value + timedelta(days=1) if upper_bound else value
        boundary = datetime.combine(day, time.min)
        if settings.USE_TZ:
            boundary = timezone.make_aware(boundary, timezone.get_current_timezone())
        lookup = "lt" if upper_bound else self.lookup_expr
        return qs.filter(**{f"{self.field_name}__{lookup}": boundary})


class CommaSeparatedIDsFilter(django_filters.CharFilter):
    """Accept a comma-separated list of integer IDs and filter with ``__in``."""

    def filter(self, qs, value):
        if not value:
            return qs
        try:
            ids = [int(v.strip()) for v in value.split(",") if v.strip()]
        except (ValueError, TypeError):
            return qs
        if not ids:
            return qs
        return qs.filter(**{f"{self.field_name}__in": ids})


class IsEmptyFilter(django_filters.BooleanFilter):
    """Filter that checks both NULL and empty string for a field."""

    def filter(self, qs, value):
        if value is None:
            return qs
        empty_q = Q(**{f"{self.field_name}__isnull": True}) | Q(
            **{f"{self.field_name}__exact": ""}
        )
        return qs.filter(empty_q) if value else qs.exclude(empty_q)


def add_is_empty_filters(filterset):
    """Add ``<name>__isempty`` BooleanFilter siblings for every base
    CharFilter (those whose param name contains no ``__``) that does
    not use a custom method.  For NumberFilter base fields, adds an
    ``isnull`` lookup instead (numbers have no empty-string concept)."""
    for name, filt in list(filterset.filters.items()):
        if "__" in name or filt.method is not None or not filt.field_name:
            continue
        isempty_name = f"{name}__isempty"
        if isempty_name in filterset.filters:
            continue
        if isinstance(filt, django_filters.CharFilter):
            filterset.filters[isempty_name] = IsEmptyFilter(field_name=filt.field_name)
        elif isinstance(filt, django_filters.NumberFilter):
            filterset.filters[isempty_name] = django_filters.BooleanFilter(
                field_name=filt.field_name, lookup_expr="isnull"
            )


class IsEmptyAutoMixin:
    """Mixin for FilterSet subclasses that auto-generates ``__isempty``
    filters for every base CharFilter / NumberFilter field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_is_empty_filters(self)
