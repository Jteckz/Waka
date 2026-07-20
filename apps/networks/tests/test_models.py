import pytest
from django.db import IntegrityError

from apps.networks.models import Network


class TestNetworkModel:
    @pytest.mark.django_db
    def test_str_representation(self):
        network = Network.objects.create(name="TestNet", network_type="TELECOM")
        assert str(network) == "TestNet"

    @pytest.mark.django_db
    def test_name_unique_constraint(self):
        Network.objects.create(name="UniqueNet", network_type="BANK")
        with pytest.raises(IntegrityError):
            Network.objects.create(name="UniqueNet", network_type="TELECOM")
