"""Tests for contracts_backend account app."""
import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from account.models import CustomUser, Role
from account.filters import UsersFilter
from account.serializers import (
    CreateAccountSerializer,
    ProfilePutSerializer,
    UsersListSerializer,
    ProfileGETSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,
)


pytestmark = pytest.mark.django_db


def make_staff_user(email="staff@test.com", password="securepass123"):
    """Create a staff user with JWT token."""
    user = CustomUser.objects.create_user(
        email=email, password=password, is_staff=True
    )
    token = str(AccessToken.for_user(user))
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return user, client


def make_regular_user(email="regular@test.com", password="securepass123"):
    """Create a regular (non-staff) user."""
    user = CustomUser.objects.create_user(
        email=email, password=password, is_staff=False
    )
    token = str(AccessToken.for_user(user))
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return user, client


@pytest.mark.django_db
class TestAccountAPI:
    def setup_method(self):
        self.anon_client = APIClient()
        self.user, self.auth_client = make_staff_user()

    # ── Authentication ──────────────────────────────────────────────────────

    def test_login_success(self):
        url = reverse("account:login")
        response = self.anon_client.post(
            url, {"email": self.user.email, "password": "securepass123"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_login_failure_wrong_password(self):
        url = reverse("account:login")
        response = self.anon_client.post(
            url, {"email": self.user.email, "password": "wrongpass"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_failure_nonexistent_email(self):
        url = reverse("account:login")
        response = self.anon_client.post(
            url, {"email": "nobody@example.com", "password": "pass"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout(self):
        url = reverse("account:logout")
        response = self.auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_profile_request(self):
        url = reverse("account:profil")
        response = self.anon_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ── Email Check ─────────────────────────────────────────────────────────

    def test_check_email_existing_user(self):
        url = reverse("account:check_email")
        response = self.auth_client.post(url, {"email": self.user.email})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data["details"]

    def test_check_email_nonexistent_user(self):
        url = reverse("account:check_email")
        response = self.auth_client.post(url, {"email": "new@example.com"})
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # ── Password Change ──────────────────────────────────────────────────────

    def test_password_change_success(self):
        url = reverse("account:password_change")
        self.user.default_password_set = True
        self.user.save()

        response = self.auth_client.put(
            url,
            {
                "old_password": "securepass123",
                "new_password": "newsecurepass456",
                "new_password2": "newsecurepass456",
            },
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        self.user.refresh_from_db()
        assert self.user.default_password_set is False

    def test_password_change_wrong_old_password(self):
        url = reverse("account:password_change")
        response = self.auth_client.put(
            url,
            {
                "old_password": "wrongpassword",
                "new_password": "newpass123",
                "new_password2": "newpass123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_change_mismatched_new_passwords(self):
        url = reverse("account:password_change")
        response = self.auth_client.put(
            url,
            {
                "old_password": "securepass123",
                "new_password": "newpass123",
                "new_password2": "differentpass456",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # ── Password Reset Flow ──────────────────────────────────────────────────

    def test_send_password_reset_valid_email(self):
        url = reverse("account:send_password_reset")
        response = self.anon_client.post(url, {"email": self.user.email})
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_send_password_reset_invalid_email_format(self):
        url = reverse("account:send_password_reset")
        response = self.anon_client.post(url, {"email": "not-a-valid-email"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_code_check_valid(self):
        self.user.password_reset_code = "1234"
        self.user.save()
        url = reverse("account:password_reset_detail", args=[self.user.email, "1234"])
        response = self.anon_client.get(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_password_reset_code_check_invalid(self):
        self.user.password_reset_code = "1234"
        self.user.save()
        url = reverse("account:password_reset_detail", args=[self.user.email, "wrong"])
        response = self.anon_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_put_valid(self):
        self.user.password_reset_code = "1234"
        self.user.default_password_set = True
        self.user.save()
        url = reverse("account:password_reset")
        response = self.anon_client.put(
            url,
            {
                "email": self.user.email,
                "code": "1234",
                "new_password": "newpass456",
                "new_password2": "newpass456",
            },
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        self.user.refresh_from_db()
        assert self.user.default_password_set is False

    def test_password_reset_put_invalid_code(self):
        self.user.password_reset_code = "1234"
        self.user.save()
        url = reverse("account:password_reset")
        response = self.anon_client.put(
            url,
            {
                "email": self.user.email,
                "code": "0000",
                "new_password": "newpass456",
                "new_password2": "newpass456",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # ── Profile ──────────────────────────────────────────────────────────────

    def test_get_profile(self):
        url = reverse("account:profil")
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email

    def test_patch_profile_first_name(self):
        url = reverse("account:profil")
        response = self.auth_client.patch(url, {"first_name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.first_name == "Updated"

    # ── Users Management ─────────────────────────────────────────────────────

    def test_list_users_as_staff(self):
        url = reverse("account:users_list")
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_pagination(self):
        url = reverse("account:users_list")
        response = self.auth_client.get(url, {"pagination": "true", "page_size": "5"})
        assert response.status_code == status.HTTP_200_OK

    def test_create_user_as_staff(self):
        url = reverse("account:users_list")
        response = self.auth_client.post(
            url,
            {
                "email": "newuser@test.com",
                "first_name": "New",
                "last_name": "User",
                "password": "Testpass123!",
            },
        )
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    def test_list_users_unauthenticated(self):
        url = reverse("account:users_list")
        response = self.anon_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_detail_as_staff(self):
        url = reverse("account:user_detail", args=[self.user.pk])
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email

    def test_get_user_detail_not_found(self):
        url = reverse("account:user_detail", args=[99999])
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_edit_user_as_staff(self):
        target_user = CustomUser.objects.create_user(
            email="target@test.com", password="pass"
        )
        url = reverse("account:user_detail", args=[target_user.pk])
        response = self.auth_client.patch(url, {"first_name": "Edited"})
        assert response.status_code == status.HTTP_200_OK

    def test_delete_user_as_staff(self):
        target_user = CustomUser.objects.create_user(
            email="todelete@test.com", password="pass"
        )
        url = reverse("account:user_detail", args=[target_user.pk])
        response = self.auth_client.delete(url)
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        )

    def test_list_users_not_staff_forbidden(self):
        _, regular_client = make_regular_user(email="notstaff2@test.com")
        url = reverse("account:users_list")
        response = regular_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomUserModel:
    def test_str_with_full_name(self):
        user = CustomUser.objects.create_user(
            email="str@test.com", password="pass",
            first_name="Jane", last_name="Doe"
        )
        assert str(user) == "Jane Doe"

    def test_str_with_email_only(self):
        user = CustomUser.objects.create_user(
            email="emailonly@test.com", password="pass"
        )
        assert str(user) == "emailonly@test.com"

    def test_default_permission_flags(self):
        user = CustomUser.objects.create_user(
            email="defaults@test.com", password="pass"
        )
        assert user.can_view is True
        assert user.can_print is True
        assert user.can_create is False
        assert user.can_edit is False
        assert user.can_delete is False

    def test_default_password_set_false(self):
        user = CustomUser.objects.create_user(
            email="defpwd@test.com", password="pass"
        )
        assert user.default_password_set is False

    def test_is_active_default_true(self):
        user = CustomUser.objects.create_user(
            email="active@test.com", password="pass"
        )
        assert user.is_active is True

    def test_get_absolute_avatar_img_none(self):
        user = CustomUser.objects.create_user(
            email="noavatar@test.com", password="pass"
        )
        assert user.get_absolute_avatar_img is None

    def test_get_absolute_avatar_cropped_img_none(self):
        user = CustomUser.objects.create_user(
            email="noavcrop@test.com", password="pass"
        )
        assert user.get_absolute_avatar_cropped_img is None


@pytest.mark.django_db
class TestUsersFilter:
    def test_global_search_by_email(self):
        user = CustomUser.objects.create_user(
            email="unique_filter@test.com", password="pass"
        )
        qs = CustomUser.objects.all()
        result = UsersFilter.global_search(qs, "search", "unique_filter")
        assert user in result

    def test_global_search_empty_value_returns_all(self):
        count_before = CustomUser.objects.count()
        qs = CustomUser.objects.all()
        result = UsersFilter.global_search(qs, "search", "")
        assert result.count() == count_before

    def test_global_search_whitespace_returns_all(self):
        count_before = CustomUser.objects.count()
        qs = CustomUser.objects.all()
        result = UsersFilter.global_search(qs, "search", "   ")
        assert result.count() == count_before

    def test_first_name_icontains_filter(self):
        u1 = CustomUser.objects.create_user(
            email="firstName1@test.com", password="p", first_name="Ahmed"
        )
        u2 = CustomUser.objects.create_user(
            email="firstName2@test.com", password="p", first_name="Sara"
        )
        qs = CustomUser.objects.all()
        filt = UsersFilter({"first_name__icontains": "ahmed"}, queryset=qs)
        assert u1 in filt.qs
        assert u2 not in filt.qs

    def test_is_staff_boolean_filter(self):
        u_staff = CustomUser.objects.create_user(
            email="stafffilter@test.com", password="p", is_staff=True
        )
        u_regular = CustomUser.objects.create_user(
            email="regularfilter@test.com", password="p", is_staff=False
        )
        qs = CustomUser.objects.all()
        filt = UsersFilter({"is_staff": "true"}, queryset=qs)
        assert u_staff in filt.qs
        assert u_regular not in filt.qs

    def test_gender_method_filter(self):
        u_h = CustomUser.objects.create_user(
            email="genderhomme@test.com", password="p", gender="H"
        )
        u_f = CustomUser.objects.create_user(
            email="genderfemme@test.com", password="p", gender="F"
        )
        qs = CustomUser.objects.all()
        filt = UsersFilter({"gender": "Homme"}, queryset=qs)
        assert u_h in filt.qs
        assert u_f not in filt.qs


@pytest.mark.django_db
class TestCreateAccountSerializer:
    def test_valid_data(self):
        data = {
            "email": "newserial@test.com",
            "password": "Testpass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        serializer = CreateAccountSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_email_invalid(self):
        data = {"password": "Testpass123!", "first_name": "Test"}
        serializer = CreateAccountSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_duplicate_email_invalid(self):
        CustomUser.objects.create_user(
            email="dup@test.com", password="pass"
        )
        data = {"email": "dup@test.com", "password": "Testpass123!"}
        serializer = CreateAccountSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestProfilePutSerializer:
    def test_patch_valid_first_name(self):
        user = CustomUser.objects.create_user(
            email="patchme@test.com", password="pass"
        )
        serializer = ProfilePutSerializer(
            instance=user, data={"first_name": "Patched"}, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.first_name == "Patched"
