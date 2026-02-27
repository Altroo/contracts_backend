from unittest.mock import MagicMock
from account.models import CustomUser

import pytest

from core.permissions import can_view, can_print, can_create, can_update, can_delete


def make_user(
    is_staff=False,
    can_view_flag=True,
    can_print_flag=True,
    can_create_flag=False,
    can_edit_flag=False,
    can_delete_flag=False,
):
    """Create a mock user with given permission flags."""
    user = MagicMock()
    user.is_staff = is_staff
    user.can_view = can_view_flag
    user.can_print = can_print_flag
    user.can_create = can_create_flag
    user.can_edit = can_edit_flag
    user.can_delete = can_delete_flag
    return user


class TestCanView:
    def test_staff_user_always_allowed(self):
        user = make_user(is_staff=True, can_view_flag=False)
        assert can_view(user) is True

    def test_regular_user_with_flag_true(self):
        user = make_user(is_staff=False, can_view_flag=True)
        assert can_view(user) is True

    def test_regular_user_with_flag_false(self):
        user = make_user(is_staff=False, can_view_flag=False)
        assert can_view(user) is False


class TestCanPrint:
    def test_staff_user_always_allowed(self):
        user = make_user(is_staff=True, can_print_flag=False)
        assert can_print(user) is True

    def test_regular_user_with_flag_true(self):
        user = make_user(is_staff=False, can_print_flag=True)
        assert can_print(user) is True

    def test_regular_user_with_flag_false(self):
        user = make_user(is_staff=False, can_print_flag=False)
        assert can_print(user) is False


class TestCanCreate:
    def test_staff_user_always_allowed(self):
        user = make_user(is_staff=True, can_create_flag=False)
        assert can_create(user) is True

    def test_regular_user_with_flag_true(self):
        user = make_user(is_staff=False, can_create_flag=True)
        assert can_create(user) is True

    def test_regular_user_with_flag_false(self):
        user = make_user(is_staff=False, can_create_flag=False)
        assert can_create(user) is False


class TestCanUpdate:
    def test_staff_user_always_allowed(self):
        user = make_user(is_staff=True, can_edit_flag=False)
        assert can_update(user) is True

    def test_regular_user_with_flag_true(self):
        user = make_user(is_staff=False, can_edit_flag=True)
        assert can_update(user) is True

    def test_regular_user_with_flag_false(self):
        user = make_user(is_staff=False, can_edit_flag=False)
        assert can_update(user) is False


class TestCanDelete:
    def test_staff_user_always_allowed(self):
        user = make_user(is_staff=True, can_delete_flag=False)
        assert can_delete(user) is True

    def test_regular_user_with_flag_true(self):
        user = make_user(is_staff=False, can_delete_flag=True)
        assert can_delete(user) is True

    def test_regular_user_with_flag_false(self):
        user = make_user(is_staff=False, can_delete_flag=False)
        assert can_delete(user) is False


@pytest.mark.django_db
class TestCorePermissionsWithRealUser:
    """Integration tests using real CustomUser instances."""

    def test_staff_user_can_do_everything(self):
        user = CustomUser.objects.create_user(
            email="staffperm@test.com", password="pass", is_staff=True
        )
        assert can_view(user) is True
        assert can_print(user) is True
        assert can_create(user) is True
        assert can_update(user) is True
        assert can_delete(user) is True

    def test_regular_user_defaults(self):
        """Regular user has can_view=True, can_print=True, others=False by default."""
        user = CustomUser.objects.create_user(
            email="regularperm@test.com", password="pass", is_staff=False
        )
        assert can_view(user) is True  # default True
        assert can_print(user) is True  # default True
        assert can_create(user) is False  # default False
        assert can_update(user) is False  # default False
        assert can_delete(user) is False  # default False

    def test_user_with_create_permission(self):
        user = CustomUser.objects.create_user(
            email="createperm@test.com",
            password="pass",
            is_staff=False,
            can_create=True,
        )
        assert can_create(user) is True
        assert can_update(user) is False

    def test_user_with_all_permissions(self):
        user = CustomUser.objects.create_user(
            email="allperms@test.com",
            password="pass",
            is_staff=False,
            can_view=True,
            can_print=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
        )
        assert can_view(user) is True
        assert can_print(user) is True
        assert can_create(user) is True
        assert can_update(user) is True
        assert can_delete(user) is True
