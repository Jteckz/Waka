import random

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.accounts.models import User
from apps.agents.models import AgentNetworkStatus, MasterAgentProfile
from apps.agents.selectors import (
    get_master_agent_profile,
    list_network_statuses,
    search_nearby_master_agents,
)
from apps.networks.models import Network
from common.constants import RoleChoices


def make_master(**overrides):
    phone = f"+25572{random.randint(10_000_000, 99_999_999)}"
    user = User.objects.create_user(
        phone=phone, password="testpass1", role=RoleChoices.MASTER_AGENT
    )
    profile = MasterAgentProfile.objects.get(user=user)
    for key, val in overrides.items():
        setattr(profile, key, val)
    if overrides:
        profile.save(update_fields=list(overrides.keys()))
    return profile


def make_minor():
    phone = f"+25573{random.randint(10_000_000, 99_999_999)}"
    return User.objects.create_user(
        phone=phone, password="testpass1", role=RoleChoices.MINOR_AGENT
    )


@pytest.mark.django_db
class TestGetProfiles:
    def test_get_master(self):
        profile = make_master()
        assert get_master_agent_profile(profile.user) == profile

    def test_get_master_not_found(self):
        user = make_minor()
        assert get_master_agent_profile(user) is None


@pytest.mark.django_db
class TestListNetworkStatuses:
    def test_lists_statuses(self):
        profile = make_master()
        net = Network.objects.create(name="Net1", network_type="TELECOM")
        AgentNetworkStatus.objects.create(
            master_agent=profile, network=net, is_active=True
        )
        statuses = list_network_statuses(profile)
        assert len(statuses) == 1
        assert statuses[0].network.name == "Net1"


@pytest.mark.django_db
class TestSearchNearbyMasterAgents:
    origin = (-6.8130, 39.2880)  # Posta, Dar es Salaam

    def test_inactive_agents_excluded(self):
        active = make_master(latitude=-6.8120, longitude=39.2890, is_active=True)
        make_master(latitude=-6.8125, longitude=39.2885, is_active=False)

        result = list(search_nearby_master_agents(self.origin, 10))
        assert active in result
        assert len(result) == 1

    def test_filters_by_radius(self):
        within = make_master(latitude=-6.7820, longitude=39.2650)  # ~4 km
        make_master(latitude=-6.4330, longitude=38.9000)  # ~40 km

        result = list(search_nearby_master_agents(self.origin, 10))
        assert within in result
        assert len(result) == 1

    def test_filters_by_network(self):
        net_a = Network.objects.create(name="Voda-Net", network_type="TELECOM")
        net_b = Network.objects.create(name="Airtel-Net", network_type="TELECOM")

        a = make_master(latitude=-6.8120, longitude=39.2890)
        AgentNetworkStatus.objects.create(master_agent=a, network=net_a, is_active=True)

        b = make_master(latitude=-6.8110, longitude=39.2880)
        AgentNetworkStatus.objects.create(master_agent=b, network=net_b, is_active=True)

        result = list(search_nearby_master_agents(self.origin, 5, network_id=net_a.id))
        assert a in result
        assert b not in result

    def test_inactive_network_status_excluded(self):
        net = Network.objects.create(name="TestNet", network_type="TELECOM")
        a = make_master(latitude=-6.8120, longitude=39.2890)
        AgentNetworkStatus.objects.create(master_agent=a, network=net, is_active=False)

        result = list(search_nearby_master_agents(self.origin, 5, network_id=net.id))
        assert a not in result

    def test_filters_by_search_query(self):
        make_master(
            business_name="Mlimani Groceries",
            latitude=-6.8120,
            longitude=39.2890,
        )
        make_master(
            business_name="Kariakoo Mart",
            latitude=-6.8110,
            longitude=39.2880,
        )

        result = list(search_nearby_master_agents(self.origin, 10, search_query="groc"))
        assert len(result) == 1
        assert "groc" in result[0].business_name.lower()

    def test_orders_by_distance(self):
        far = make_master(latitude=-6.8190, longitude=39.2780)
        near = make_master(latitude=-6.8120, longitude=39.2890)

        result = list(search_nearby_master_agents(self.origin, 10))
        assert result[0] == near
        assert result[1] == far
        assert result[0].distance < result[1].distance

    def test_annotates_distance_in_km(self):
        # ~1 degree = ~111 km; 0.01 deg ~ 1.1 km
        make_master(latitude=-6.8130, longitude=39.2880)

        result = list(search_nearby_master_agents(self.origin, 10))
        assert len(result) == 1
        dist = result[0].distance
        assert dist is not None
        assert 0 <= dist <= 0.01  # same point, should be ~0

    def test_network_and_search_combined(self):
        net = Network.objects.create(name="Voda", network_type="TELECOM")
        a = make_master(
            business_name="Mlimani Water",
            latitude=-6.8120,
            longitude=39.2890,
        )
        AgentNetworkStatus.objects.create(master_agent=a, network=net, is_active=True)
        b = make_master(
            business_name="Mlimani Food",
            latitude=-6.7820,
            longitude=39.2650,
        )
        AgentNetworkStatus.objects.create(master_agent=b, network=net, is_active=True)

        result = list(
            search_nearby_master_agents(
                self.origin, 5, network_id=net.id, search_query="water"
            )
        )
        assert len(result) == 1
        assert "water" in result[0].business_name.lower()

    def test_nearby_empty_when_no_matches(self):
        make_master(latitude=-6.4330, longitude=38.9000)

        result = list(search_nearby_master_agents(self.origin, 1))
        assert len(result) == 0

    def test_query_count_does_not_grow_with_results(self):
        net = Network.objects.create(name="Net", network_type="TELECOM")
        agents = []
        for i in range(5):
            a = make_master(latitude=-6.81 + i * 0.002, longitude=39.28 + i * 0.002)
            agents.append(a)
            AgentNetworkStatus.objects.create(
                master_agent=a, network=net, is_active=True
            )

        with CaptureQueriesContext(connection) as ctx:
            list(search_nearby_master_agents(self.origin, 10, network_id=net.id))
        n_queries = len(ctx.captured_queries)
        assert n_queries <= 5, f"Expected ≤5 queries, got {n_queries}"
