import factory
from django.contrib.auth.hashers import make_password

from apps.accounts.models import User
from common.constants import RoleChoices


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    phone = factory.Sequence(lambda n: f"+998901{n:07d}")
    role = RoleChoices.MINOR_AGENT
    password = factory.LazyFunction(lambda: make_password("testpass1"))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return User.objects.create_user(*args, **kwargs)

    class Params:
        master = factory.Trait(role=RoleChoices.MASTER_AGENT)
        minor = factory.Trait(role=RoleChoices.MINOR_AGENT)
        admin = factory.Trait(role=RoleChoices.ADMIN)
