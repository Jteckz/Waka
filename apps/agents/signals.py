from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from apps.agents.services import create_master_agent_profile, create_minor_agent_profile
from common.constants import RoleChoices


@receiver(post_save, sender=User)
def auto_create_profile(sender, instance, created, **kwargs):
    """Automatically create the appropriate agent profile when a User is created.

    Tradeoff: using a signal instead of a direct service call from
    accounts.services.register_user avoids a circular import (accounts
    is more foundational than agents). The downside is implicit coupling:
    profile creation happens outside the request-response cycle, which can
    surprise developers debugging registration flows.
    """
    if not created:
        return

    if instance.role == RoleChoices.MASTER_AGENT:
        create_master_agent_profile(
            user=instance,
            business_name=instance.phone,
        )
    elif instance.role == RoleChoices.MINOR_AGENT:
        create_minor_agent_profile(user=instance)
