import factory

from apps.agents.models import AgentNetworkStatus


class AgentNetworkStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AgentNetworkStatus

    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.objects.get_or_create(**kwargs)[0]
