import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from common.constants import RoleChoices

User = get_user_model()

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/login/refresh"
ME_URL = "/api/v1/auth/me"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_credentials():
    return {
        "phone": "+255712000000",
        "password": "StrongPass1",
        "role": RoleChoices.MASTER_AGENT,
    }


class TestRegister:
    @pytest.mark.django_db
    def test_successful_registration(self, api_client):
        data = {
            "phone": "+255712000001",
            "password": "StrongPass1",
            "role": RoleChoices.MASTER_AGENT,
        }
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["phone"] == "+255712000001"
        assert response.data["user"]["role"] == RoleChoices.MASTER_AGENT

    @pytest.mark.django_db
    def test_duplicate_phone(self, api_client):
        data = {
            "phone": "+255712000002",
            "password": "StrongPass2",
            "role": RoleChoices.MINOR_AGENT,
        }
        api_client.post(REGISTER_URL, data, format="json")
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_weak_password(self, api_client):
        data = {
            "phone": "+255712000003",
            "password": "123",
            "role": RoleChoices.MINOR_AGENT,
        }
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_missing_fields(self, api_client):
        response = api_client.post(REGISTER_URL, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_invalid_role(self, api_client):
        data = {"phone": "+255712000004", "password": "StrongPass4", "role": "INVALID"}
        response = api_client.post(REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    @pytest.mark.django_db
    def test_successful_login(self, api_client, user_credentials):
        User.objects.create_user(**user_credentials)
        response = api_client.post(LOGIN_URL, user_credentials, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    @pytest.mark.django_db
    def test_login_wrong_password(self, api_client, user_credentials):
        User.objects.create_user(**user_credentials)
        response = api_client.post(
            LOGIN_URL,
            {"phone": user_credentials["phone"], "password": "WrongPass1"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_login_wrong_phone(self, api_client):
        response = api_client.post(
            LOGIN_URL,
            {"phone": "+255999999999", "password": "SomePass1"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    @pytest.mark.django_db
    def test_successful_refresh(self, api_client, user_credentials):
        User.objects.create_user(**user_credentials)
        login_resp = api_client.post(LOGIN_URL, user_credentials, format="json")
        refresh_token = login_resp.data["refresh"]
        response = api_client.post(
            REFRESH_URL, {"refresh": refresh_token}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


class TestMe:
    @pytest.mark.django_db
    def test_authenticated(self, api_client, user_credentials):
        User.objects.create_user(**user_credentials)
        login_resp = api_client.post(LOGIN_URL, user_credentials, format="json")
        access_token = login_resp.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.get(ME_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["phone"] == user_credentials["phone"]
        assert response.data["role"] == user_credentials["role"]

    @pytest.mark.django_db
    def test_unauthenticated(self, api_client):
        response = api_client.get(ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
