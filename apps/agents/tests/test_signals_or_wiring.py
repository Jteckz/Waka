import pytest

from apps.accounts.services import register_user
from apps.agents.models import MasterAgentProfile, MinorAgentProfile
from common.constants import RoleChoices


@pytest.mark.django_db
class TestAutoProfileCreation:
    def test_register_master_agent_creates_profile(self):
        user = register_user(
            phone="+255713000001",
            password="testpass123",
            role=RoleChoices.MASTER_AGENT,
        )
        profile = MasterAgentProfile.objects.filter(user=user).first()
        assert profile is not None
        assert profile.business_name == user.phone

    def test_register_minor_agent_creates_profile(self):
        user = register_user(
            phone="+255713000002",
            password="testpass123",
            role=RoleChoices.MINOR_AGENT,
        )
        profile = MinorAgentProfile.objects.filter(user=user).first()
        assert profile is not None
