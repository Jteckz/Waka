import pytest
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from apps.accounts.models import User
from apps.agents.models import AgentNetworkStatus, MasterAgentProfile, MinorAgentProfile
from apps.networks.models import Network


@pytest.mark.django_db
class TestMasterAgentProfile:
    def test_one_profile_per_user(self):
        user = User.objects.create_user(
            phone="+255711000001", password="testpass1", role="MASTER_AGENT"
        )
        with pytest.raises(IntegrityError):
            MasterAgentProfile.objects.create(user=user, business_name="Second Biz")

    def test_on_delete_protect(self):
        user = User.objects.create_user(
            phone="+255711000002", password="testpass1", role="MASTER_AGENT"
        )
        with pytest.raises(ProtectedError):
            user.delete()


@pytest.mark.django_db
class TestMinorAgentProfile:
    def test_one_profile_per_user(self):
        user = User.objects.create_user(
            phone="+255711000010", password="testpass1", role="MINOR_AGENT"
        )
        with pytest.raises(IntegrityError):
            MinorAgentProfile.objects.create(user=user)

    def test_on_delete_protect(self):
        user = User.objects.create_user(
            phone="+255711000011", password="testpass1", role="MINOR_AGENT"
        )
        with pytest.raises(ProtectedError):
            user.delete()


@pytest.mark.django_db
class TestAgentNetworkStatus:
    def test_unique_per_agent_network_pair(self):
        user = User.objects.create_user(
            phone="+255711000020", password="testpass1", role="MASTER_AGENT"
        )
        profile = MasterAgentProfile.objects.get(user=user)
        network = Network.objects.create(name="TestNet", network_type="TELECOM")
        AgentNetworkStatus.objects.create(master_agent=profile, network=network)
        with pytest.raises(IntegrityError):
            AgentNetworkStatus.objects.create(master_agent=profile, network=network)
