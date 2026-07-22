from rest_framework import serializers

from apps.agents.models import AgentNetworkStatus, MasterAgentProfile, MinorAgentProfile


class MasterAgentProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = MasterAgentProfile
        fields = [
            "id",
            "phone",
            "business_name",
            "profile_photo",
            "business_photos",
            "is_active",
            "response_rate",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "response_rate",
            "created_at",
            "updated_at",
        ]


class MinorAgentProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = MinorAgentProfile
        fields = ["id", "phone", "display_name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AgentNetworkStatusSerializer(serializers.ModelSerializer):
    network_id = serializers.UUIDField(write_only=True)
    network_name = serializers.CharField(source="network.name", read_only=True)

    class Meta:
        model = AgentNetworkStatus
        fields = [
            "id",
            "network_id",
            "network_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class _ActiveNetworkBriefSerializer(serializers.ModelSerializer):
    network_name = serializers.CharField(source="network.name")

    class Meta:
        model = AgentNetworkStatus
        fields = ["id", "network_name", "is_active"]


class MasterAgentNearbySerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True)
    active_networks = serializers.SerializerMethodField()

    class Meta:
        model = MasterAgentProfile
        fields = [
            "id",
            "business_name",
            "profile_photo",
            "latitude",
            "longitude",
            "response_rate",
            "distance",
            "active_networks",
        ]

    def get_active_networks(self, obj):
        statuses = getattr(obj, "_prefetched_active_statuses", [])
        return _ActiveNetworkBriefSerializer(statuses, many=True).data
