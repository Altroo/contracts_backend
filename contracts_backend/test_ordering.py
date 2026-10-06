from decimal import Decimal
import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from account.views import UsersListCreateView
from contracts_backend.ordering import apply_list_ordering, fields_for

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("model", ["accounts.CustomUser", "contract.Contract"])
def test_every_public_ordering_expression_executes(model):
    qs = apps.get_model(model).objects.all()
    _, fields = fields_for(qs, "", {"store": "1"})
    assert fields
    for field in fields:
        for prefix in ["", "-"]:
            list(
                apply_list_ordering(qs, {"ordering": prefix + field, "store": "1"})[:2]
            )


def test_api_sorts_complete_result_before_pagination_and_keeps_filter():
    User = get_user_model()
    admin = User.objects.create_user(
        email="sort-admin@example.test", password="test", is_staff=True
    )
    names = ["Zulu", "Bravo", "Echo", "alpha", "Delta", "Charlie", "Foxtrot"]
    for i, name in enumerate(names):
        User.objects.create_user(
            email=f"sort-{i}@example.test",
            password="test",
            first_name=name,
            last_name="included",
        )
    User.objects.create_user(
        email="sort-excluded@example.test",
        password="test",
        first_name="AAA",
        last_name="excluded",
    )
    factory = APIRequestFactory()

    def page(ordering, number=1):
        request = factory.get(
            "/",
            {
                "pagination": "true",
                "page": number,
                "page_size": 5,
                "ordering": ordering,
                "last_name": "included",
            },
        )
        force_authenticate(request, admin)
        response = UsersListCreateView.as_view()(request)
        assert response.status_code == 200, response.data
        assert response.data["count"] == 7
        return [row["first_name"] for row in response.data["results"]]

    expected = sorted(names, key=str.casefold)
    assert page("first_name") + page("first_name", 2) == expected
    assert page("-first_name") + page("-first_name", 2) == expected[::-1]


@pytest.mark.parametrize(
    "ordering",
    [
        "password",
        "-password",
        "groups__name",
        "first_name,-id",
        "id; DROP TABLE account",
        "-",
    ],
)
def test_unknown_columns_cannot_order_private_or_related_data(ordering):
    qs = get_user_model().objects.order_by("-id")
    assert str(apply_list_ordering(qs, {"ordering": ordering}).query) == str(qs.query)


def test_contract_amounts_sort_numerically_with_stable_ties():
    from datetime import date
    from contract.models import Contract

    rows = [
        Contract.objects.create(
            numero_contrat=f"SORT-{i}",
            client_nom=f"Client {i}",
            date_contrat=date(2026, 1, 1),
            montant_ht=value,
        )
        for i, value in enumerate([100, 2, 10, 10])
    ]
    assert list(
        apply_list_ordering(Contract.objects.all(), {"ordering": "montant_ht"})
    ) == [rows[1], rows[2], rows[3], rows[0]]
    assert list(
        apply_list_ordering(Contract.objects.all(), {"ordering": "-montant_ht"})
    ) == [rows[0], rows[3], rows[2], rows[1]]
