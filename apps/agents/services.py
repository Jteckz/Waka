from apps.agents.models import AgentNetworkStatus, MasterAgentProfile, MinorAgentProfile
from apps.geo.utils import validate_latitude, validate_longitude
from common.constants import RoleChoices
from common.exceptions import ValidationError


def create_master_agent_profile(user, business_name, **fields):
    if user.role != RoleChoices.MASTER_AGENT:
        raise ValidationError(
            f"Cannot create MasterAgentProfile for user with role '{user.role}'"
        )
    if MasterAgentProfile.objects.filter(user=user).exists():
        raise ValidationError("MasterAgentProfile already exists for this user")
    return MasterAgentProfile.objects.create(
        user=user, business_name=business_name, **fields
    )


def create_minor_agent_profile(user, **fields):
    if user.role != RoleChoices.MINOR_AGENT:
        raise ValidationError(
            f"Cannot create MinorAgentProfile for user with role '{user.role}'"
        )
    if MinorAgentProfile.objects.filter(user=user).exists():
        raise ValidationError("MinorAgentProfile already exists for this user")
    return MinorAgentProfile.objects.create(user=user, **fields)


def update_master_agent_location(profile, latitude, longitude):
    validate_latitude(latitude)
    validate_longitude(longitude)
    profile.set_coordinates(latitude, longitude)
    profile.save(update_fields=["latitude", "longitude", "updated_at"])


def set_agent_active_status(profile, is_active):
    profile.is_active = is_active
    profile.save(update_fields=["is_active", "updated_at"])


def set_network_status(master_agent_profile, network, is_active):
    status, _ = AgentNetworkStatus.objects.get_or_create(
        master_agent=master_agent_profile,
        network=network,
    )
    status.is_active = is_active
    status.save(update_fields=["is_active", "updated_at"])
    return status
