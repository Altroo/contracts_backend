from re import search

from django.db import transaction
from django.utils import timezone

from core.utils import format_number_with_dynamic_digits
from .models import Contract


def get_next_numero_contrat(company: str = "", contract_category: str = "") -> str:
    """
    Return the next available numero_contrat string like '0001/26'.
    Scoped by company and contract_category for uniqueness.
    Automatically increases digit count when 9999 is reached.
    """
    year_suffix = f"{timezone.localtime(timezone.now()).year % 100:02d}"

    with transaction.atomic():
        qs = Contract.objects.filter(
            numero_contrat__isnull=False,
            numero_contrat__endswith=f"/{year_suffix}",
        )
        if company:
            qs = qs.filter(company=company)
        if contract_category:
            qs = qs.filter(contract_category=contract_category)

        existing = qs.select_for_update().values_list("numero_contrat", flat=True)

        used_numbers = []
        for raw in existing:
            m = search(r"^(\d+)/\d{2}$", raw or "")
            if m:
                try:
                    used_numbers.append(int(m.group(1)))
                except ValueError:
                    continue

        used_numbers = sorted(set(used_numbers))
        next_number = None
        for i in range(1, (max(used_numbers) if used_numbers else 0) + 2):
            if i not in used_numbers:
                next_number = i
                break

        formatted_number = format_number_with_dynamic_digits(next_number, min_digits=4)
        return f"{formatted_number}/{year_suffix}"
