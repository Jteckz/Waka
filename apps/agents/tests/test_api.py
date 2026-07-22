import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.agents.models import MasterAgentProfile
from apps.networks.models import Network
from common.constants import RoleChoices


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def master_user():
    return User.objects.create_user(
        phone="+255714000001", password="testpass1", role=RoleChoices.MASTER_AGENT
    )


@pytest.fixture
def minor_user():
    return User.objects.create_user(
        phone="+255714000002", password="testpass1", role=RoleChoices.MINOR_AGENT
    )


@pytest.mark.django_db
class TestMasterProfileEndpoint:
    def test_get_profile(self, client, master_user):
        client.force_authenticate(user=master_user)
        resp = client.get("/api/v1/agents/master/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["phone"] == "+255714000001"
        assert data["business_name"] == "+255714000001"

    def test_denies_minor_agent(self, client, minor_user):
        client.force_authenticate(user=minor_user)
        resp = client.get("/api/v1/agents/master/me")
        assert resp.status_code == 403

    def test_denies_unauthenticated(self, client):
        resp = client.get("/api/v1/agents/master/me")
        assert resp.status_code == 401

    def test_patch_profile(self, client, master_user):
        client.force_authenticate(user=master_user)
        resp = client.patch(
            "/api/v1/agents/master/me",
            {"business_name": "Updated Biz"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["business_name"] == "Updated Biz"


@pytest.mark.django_db
class TestMinorProfileEndpoint:
    def test_get_profile(self, client, minor_user):
        client.force_authenticate(user=minor_user)
        resp = client.get("/api/v1/agents/minor/me")
        assert resp.status_code == 200
        assert resp.json()["phone"] == "+255714000002"

    def test_denies_master_agent(self, client, master_user):
        client.force_authenticate(user=master_user)
        resp = client.get("/api/v1/agents/minor/me")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestNetworkStatusEndpoint:
    def test_post_network_status(self, client, master_user):
        network = Network.objects.create(name="TestNet", network_type="TELECOM")
        client.force_authenticate(user=master_user)
        resp = client.post(
            "/api/v1/agents/master/network-status",
            {"network_id": str(network.id), "is_active": True},
            format="json",
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["network_name"] == "TestNet"
        assert data["is_active"] is True

    def test_list_network_statuses(self, client, master_user):
        network = Network.objects.create(name="Net2", network_type="BANK")
        profile = MasterAgentProfile.objects.get(user=master_user)
        profile.network_statuses.create(network=network, is_active=True)
        client.force_authenticate(user=master_user)
        resp = client.get("/api/v1/agents/master/network-status")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["network_name"] == "Net2"


@pytest.fixture
def many_master_agents():
    """Create master agents near Posta, Dar es Salaam."""
    from apps.agents.tests.test_selectors import make_master

    agents = []
    offsets = [
        (-6.8130, 39.2880, "Posta Main"),
        (-6.8140, 39.2890, "Posta Branch"),
        (-6.8150, 39.2900, "Posta Express"),
        (-6.8100, 39.2850, "Kivukoni Agent"),
        (-6.7800, 39.2600, "Upanga Agent"),  # ~4 km
    ]
    for lat, lng, name in offsets:
        agents.append(make_master(business_name=name, latitude=lat, longitude=lng))
    return agents


@pytest.mark.django_db
class TestNearbyMasterAgentsEndpoint:
    def test_requires_auth(self, client):
        resp = client.get("/api/v1/agents/master/nearby?lat=-6.813&lng=39.288")
        assert resp.status_code == 401

    def test_requires_minor_agent(self, client, master_user):
        client.force_authenticate(user=master_user)
        resp = client.get("/api/v1/agents/master/nearby?lat=-6.813&lng=39.288")
        assert resp.status_code == 403

    def test_requires_lat_lng(self, client, minor_user):
        client.force_authenticate(user=minor_user)
        resp = client.get("/api/v1/agents/master/nearby")
        assert resp.status_code == 400
        body = resp.json()["error"]["message"].lower()
        assert "lat" in body or "lng" in body

    def test_requires_numeric_lat_lng(self, client, minor_user):
        client.force_authenticate(user=minor_user)
        resp = client.get("/api/v1/agents/master/nearby?lat=abc&lng=39.288")
        assert resp.status_code == 400

    def test_caps_radius(self, client, minor_user):
        client.force_authenticate(user=minor_user)
        resp = client.get(
            "/api/v1/agents/master/nearby?lat=-6.813&lng=39.288&radius_km=999"
        )
        assert resp.status_code == 400

    def test_returns_paginated_results(self, client, minor_user, many_master_agents):
        client.force_authenticate(user=minor_user)
        resp = client.get(
            "/api/v1/agents/master/nearby?lat=-6.813&lng=39.288&radius_km=5"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) <= 10
        assert data["results"][0]["business_name"] == "Posta Main"

    def test_distance_precision(self, client, minor_user):
        from apps.accounts.models import User
        from apps.agents.models import MasterAgentProfile

        user = User.objects.create_user(
            phone="+255719999001", password="testpass1", role=RoleChoices.MASTER_AGENT
        )
        profile = MasterAgentProfile.objects.get(user=user)
        profile.business_name = "Test Agent"
        profile.latitude = -6.8130
        profile.longitude = 39.2880
        profile.save()

        client.force_authenticate(user=minor_user)
        resp = client.get(
            "/api/v1/agents/master/nearby?lat=-6.8130&lng=39.2880&radius_km=1"
        )
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert "distance" in result
        assert 0 <= result["distance"] <= 0.01

    def test_includes_active_networks(self, client, minor_user):
        from apps.agents.models import AgentNetworkStatus
        from apps.agents.tests.test_selectors import make_master

        net = Network.objects.create(name="TestNet", network_type="TELECOM")
        agent = make_master(
            business_name="Net Agent", latitude=-6.8130, longitude=39.2880
        )
        AgentNetworkStatus.objects.create(
            master_agent=agent, network=net, is_active=True
        )
        client.force_authenticate(user=minor_user)
        resp = client.get(
            "/api/v1/agents/master/nearby?lat=-6.813&lng=39.288&radius_km=1"
        )
        data = resp.json()["results"][0]
        assert "active_networks" in data
        assert len(data["active_networks"]) == 1
        assert data["active_networks"][0]["network_name"] == "TestNet"


@pytest.mark.django_db
class TestMasterAgentDetailEndpoint:
    def test_retrieves_active_master(self, client, minor_user):
        from apps.agents.tests.test_selectors import make_master

        agent = make_master(business_name="Detail Agent")
        client.force_authenticate(user=minor_user)
        resp = client.get(f"/api/v1/agents/master/{agent.id}")
        assert resp.status_code == 200
        assert resp.json()["business_name"] == "Detail Agent"

    def test_404_for_inactive_agent(self, client, minor_user):
        from apps.agents.tests.test_selectors import make_master

        agent = make_master(is_active=False)
        client.force_authenticate(user=minor_user)
        resp = client.get(f"/api/v1/agents/master/{agent.id}")
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        from apps.agents.tests.test_selectors import make_master

        agent = make_master()
        resp = client.get(f"/api/v1/agents/master/{agent.id}")
        assert resp.status_code == 401

    def test_404_for_nonexistent(self, client, minor_user):
        import uuid

        client.force_authenticate(user=minor_user)
        resp = client.get(f"/api/v1/agents/master/{uuid.uuid4()}")
        assert resp.status_code == 404
