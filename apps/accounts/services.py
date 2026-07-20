from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.accounts.models import User
from common.constants import RoleChoices
from common.exceptions import ValidationError


def register_user(phone, password, role, **extra_fields):
    if role not in (RoleChoices.MASTER_AGENT, RoleChoices.MINOR_AGENT):
        raise ValidationError(
            f"Invalid role '{role}'. Must be MASTER_AGENT or MINOR_AGENT."
        )

    if phone and User.objects.filter(phone=phone).exists():
        raise ValidationError(f"A user with phone '{phone}' already exists.")

    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise ValidationError(
            message="Password validation failed", details={"password": e.messages}
        ) from None

    user = User.objects.create_user(
        phone=phone, password=password, role=role, **extra_fields
    )

    # TODO: Create MasterAgentProfile / MinorAgentProfile based on role.
    # This will be wired via a post_save signal or explicit call once apps/agents exists.  # noqa: E501
    # from apps.agents.services import create_agent_profile
    # create_agent_profile(user)

    return user
