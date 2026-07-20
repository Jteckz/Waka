from rest_framework import serializers

from apps.networks.models import Network


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ["id", "name", "logo", "network_type"]
