from django.conf import settings
from django.db import models

from apps.geo.models import GeoLocatedModel
from common.models import BaseModel


class MasterAgentProfile(BaseModel, GeoLocatedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="master_profile",
    )
    business_name = models.CharField(max_length=200, db_index=True)
    profile_photo = models.URLField(max_length=500, blank=True, default="")
    business_photos = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    response_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=None
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} ({self.user.phone})"


class MinorAgentProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="minor_profile"
    )
    display_name = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.display_name or self.user.phone}"


class AgentNetworkStatus(BaseModel):
    master_agent = models.ForeignKey(
        MasterAgentProfile,
        on_delete=models.CASCADE,
        related_name="network_statuses",
    )
    network = models.ForeignKey(
        "networks.Network",
        on_delete=models.PROTECT,
        related_name="agent_statuses",
    )
    is_active = models.BooleanField(default=False, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["master_agent", "network"],
                name="uq_master_agent_network",
            )
        ]
        ordering = ["master_agent", "network"]

    def __str__(self):
        active = "active" if self.is_active else "inactive"
        return f"{self.master_agent.business_name} - {self.network.name}: {active}"
