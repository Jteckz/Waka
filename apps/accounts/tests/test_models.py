import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from common.constants import RoleChoices

User = get_user_model()


class TestUserCreation:
    @pytest.mark.django_db
    def test_create_user_with_phone(self):
        user = User.objects.create_user(
            phone="+255712000000", password="testpass123", role=RoleChoices.MASTER_AGENT
        )
        assert user.phone == "+255712000000"
        assert user.role == RoleChoices.MASTER_AGENT
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("testpass123") is True

    @pytest.mark.django_db
    def test_create_user_defaults_to_minor_agent(self):
        user = User.objects.create_user(phone="+255712000001", password="testpass123")
        assert user.role == RoleChoices.MINOR_AGENT

    @pytest.mark.django_db
    def test_create_superuser(self):
        user = User.objects.create_superuser(
            phone="+255712000002", password="adminpass123"
        )
        assert user.role == RoleChoices.ADMIN
        assert user.is_staff is True
        assert user.is_superuser is True

    @pytest.mark.django_db
    def test_phone_is_unique(self):
        User.objects.create_user(phone="+255712000003", password="testpass123")
        with pytest.raises(IntegrityError):
            User.objects.create_user(phone="+255712000003", password="testpass456")

    @pytest.mark.django_db
    def test_user_str_is_phone(self):
        user = User.objects.create_user(phone="+255712000004", password="testpass123")
        assert str(user) == "+255712000004"

    @pytest.mark.django_db
    def test_requires_phone(self):
        with pytest.raises(ValueError, match="Phone number is required"):
            User.objects.create_user(phone="", password="testpass123")

    @pytest.mark.django_db
    def test_requires_role(self):
        user = User.objects.create_user(phone="+255712000005", password="testpass123")
        assert user.role is not None
