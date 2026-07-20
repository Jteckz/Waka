import pytest
from django.contrib.auth import get_user_model

from apps.accounts.services import register_user
from common.constants import RoleChoices
from common.exceptions import ValidationError

User = get_user_model()


class TestRegisterUser:
    @pytest.mark.django_db
    def test_register_master_agent(self):
        user = register_user(
            phone="+255712000000", password="StrongPass1", role=RoleChoices.MASTER_AGENT
        )
        assert user.phone == "+255712000000"
        assert user.role == RoleChoices.MASTER_AGENT
        assert user.check_password("StrongPass1") is True

    @pytest.mark.django_db
    def test_register_minor_agent(self):
        user = register_user(
            phone="+255712000001", password="StrongPass2", role=RoleChoices.MINOR_AGENT
        )
        assert user.role == RoleChoices.MINOR_AGENT

    @pytest.mark.django_db
    def test_rejects_duplicate_phone(self):
        register_user(
            phone="+255712000002", password="StrongPass3", role=RoleChoices.MINOR_AGENT
        )
        with pytest.raises(ValidationError, match="already exists"):
            register_user(
                phone="+255712000002",
                password="StrongPass4",
                role=RoleChoices.MASTER_AGENT,
            )

    @pytest.mark.django_db
    def test_rejects_admin_role(self):
        with pytest.raises(ValidationError, match="Invalid role"):
            register_user(
                phone="+255712000003", password="StrongPass5", role=RoleChoices.ADMIN
            )

    @pytest.mark.django_db
    def test_rejects_invalid_role_string(self):
        with pytest.raises(ValidationError, match="Invalid role"):
            register_user(phone="+255712000004", password="StrongPass6", role="INVALID")

    @pytest.mark.django_db
    def test_password_validation_propagates(self):
        with pytest.raises(ValidationError, match="Password validation failed"):
            register_user(
                phone="+255712000005", password="123", role=RoleChoices.MINOR_AGENT
            )

    @pytest.mark.django_db
    def test_password_must_have_letter_and_digit(self):
        with pytest.raises(ValidationError):
            register_user(
                phone="+255712000006",
                password="allletters",
                role=RoleChoices.MINOR_AGENT,
            )
        with pytest.raises(ValidationError):
            register_user(
                phone="+255712000007", password="12345678", role=RoleChoices.MINOR_AGENT
            )
