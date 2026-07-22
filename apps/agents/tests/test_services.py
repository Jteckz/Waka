import pytest
from django.db.models.signals import post_save

from apps.accounts.models import User
from apps.agents.models import AgentNetworkStatus, MasterAgentProfile
from apps.agents.services import (
    create_master_agent_profile,
    create_minor_agent_profile,
    set_network_status,
    update_master_agent_location,
)
from apps.networks.models import Network
from common.constants import RoleChoices
from common.exceptions import ValidationError


@pytest.fixture
def no_auto_profile():
    """Disconnect the auto-profile signal for tests that create profiles manually."""
    from apps.agents.signals import auto_create_profile

    post_save.disconnect(auto_create_profile, sender=User)
    yield
    post_save.connect(auto_create_profile, sender=User)


@pytest.mark.django_db
class TestCreateMasterAgentProfile:
    @pytest.mark.usefixtures("no_auto_profile")
    def test_creates_profile_for_master_agent(self):
        user = User.objects.create_user(
            phone="+255712000001",
            password="testpass1",
            role=RoleChoices.MASTER_AGENT,
        )
        profile = create_master_agent_profile(user, business_name="My Shop")
        assert profile.user == user
        assert profile.business_name == "My Shop"

    @pytest.mark.usefixtures("no_auto_profile")
    def test_rejects_minor_agent(self):
        user = User.objects.create_user(
            phone="+255712000002",
            password="testpass1",
            role=RoleChoices.MINOR_AGENT,
        )
        with pytest.raises(ValidationError):
            create_master_agent_profile(user, business_name="My Shop")


@pytest.mark.django_db
class TestCreateMinorAgentProfile:
    @pytest.mark.usefixtures("no_auto_profile")
    def test_creates_profile_for_minor_agent(self):
        user = User.objects.create_user(
            phone="+255712000010",
            password="testpass1",
            role=RoleChoices.MINOR_AGENT,
        )
        profile = create_minor_agent_profile(user)
        assert profile.user == user

    @pytest.mark.usefixtures("no_auto_profile")
    def test_rejects_master_agent(self):
        user = User.objects.create_user(
            phone="+255712000011",
            password="testpass1",
            role=RoleChoices.MASTER_AGENT,
        )
        with pytest.raises(ValidationError):
            create_minor_agent_profile(user)


@pytest.mark.django_db
class TestUpdateMasterAgentLocation:
    @pytest.mark.usefixtures("no_auto_profile")
    def test_stores_coordinates(self):
        user = User.objects.create_user(
            phone="+255712000020",
            password="testpass1",
            role=RoleChoices.MASTER_AGENT,
        )
        profile = MasterAgentProfile.objects.create(user=user, business_name="Test")
        update_master_agent_location(profile, -6.8130, 39.2880)
        profile.refresh_from_db()
        assert profile.latitude == -6.8130
        assert profile.longitude == 39.2880


@pytest.mark.django_db
class TestSetNetworkStatus:
    @pytest.mark.usefixtures("no_auto_profile")
    def test_get_or_create_behavior(self):
        user = User.objects.create_user(
            phone="+255712000030",
            password="testpass1",
            role=RoleChoices.MASTER_AGENT,
        )
        profile = MasterAgentProfile.objects.create(user=user, business_name="Test")
        network = Network.objects.create(name="Net1", network_type="TELECOM")

        status1 = set_network_status(profile, network, is_active=True)
        assert AgentNetworkStatus.objects.count() == 1
        assert status1.is_active is True

        status2 = set_network_status(profile, network, is_active=False)
        assert AgentNetworkStatus.objects.count() == 1
        assert status2.is_active is False
