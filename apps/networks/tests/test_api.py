import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.networks.models import Network

SEEDED_NAMES = ["Airtel", "Vodacom", "Yas/Tigo", "Halotel", "CRDB", "NMB", "NBC"]


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()


@pytest.fixture
def client():
    return APIClient()


class TestNetworkList:
    @pytest.mark.django_db
    def test_returns_all_seeded_networks(self, client):
        resp = client.get("/api/v1/networks/")
        assert resp.status_code == 200
        names = [n["name"] for n in resp.json()]
        assert sorted(names) == sorted(SEEDED_NAMES)

    @pytest.mark.django_db
    def test_returns_correct_fields(self, client):
        resp = client.get("/api/v1/networks/")
        assert resp.status_code == 200
        for network in resp.json():
            assert set(network.keys()) == {"id", "name", "logo", "network_type"}

    @pytest.mark.django_db
    def test_publicly_accessible_without_auth(self, client):
        resp = client.get("/api/v1/networks/")
        assert resp.status_code == 200

    @pytest.mark.django_db
    def test_excludes_inactive_networks(self, client):
        Network.objects.filter(name="Airtel").update(is_active=False)
        resp = client.get("/api/v1/networks/")
        names = [n["name"] for n in resp.json()]
        assert "Airtel" not in names
        assert len(names) == 6

    @pytest.mark.django_db
    def test_inactive_network_excluded_even_if_created_in_test(self, client):
        Network.objects.create(name="GhostNet", network_type="TELECOM", is_active=False)
        resp = client.get("/api/v1/networks/")
        names = [n["name"] for n in resp.json()]
        assert "GhostNet" not in names
