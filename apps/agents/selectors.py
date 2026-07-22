from django.db.models import Prefetch

from apps.agents.models import AgentNetworkStatus, MasterAgentProfile, MinorAgentProfile
from apps.geo.selectors import nearby as geo_nearby


def get_master_agent_profile(user):
    try:
        return MasterAgentProfile.objects.get(user=user)
    except MasterAgentProfile.DoesNotExist:
        return None


def get_minor_agent_profile(user):
    try:
        return MinorAgentProfile.objects.get(user=user)
    except MinorAgentProfile.DoesNotExist:
        return None


def list_network_statuses(master_agent_profile):
    return master_agent_profile.network_statuses.select_related("network").all()


def search_nearby_master_agents(point, radius_km, network_id=None, search_query=None):
    qs = MasterAgentProfile.objects.filter(is_active=True)

    if network_id:
        qs = qs.filter(
            network_statuses__network_id=network_id,
            network_statuses__is_active=True,
        )

    if search_query:
        qs = qs.filter(business_name__icontains=search_query)

    qs = geo_nearby(qs, point, radius_km, lat_field="latitude", lng_field="longitude")

    active_statuses = Prefetch(
        "network_statuses",
        queryset=AgentNetworkStatus.objects.filter(is_active=True).select_related(
            "network"
        ),
        to_attr="_prefetched_active_statuses",
    )

    return qs.select_related("user").prefetch_related(active_statuses)
