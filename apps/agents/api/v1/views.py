from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.agents.api.v1.serializers import (
    AgentNetworkStatusSerializer,
    MasterAgentNearbySerializer,
    MasterAgentProfileSerializer,
    MinorAgentProfileSerializer,
)
from apps.agents.models import MasterAgentProfile
from apps.agents.selectors import list_network_statuses, search_nearby_master_agents
from apps.agents.services import set_network_status
from apps.geo.utils import validate_latitude, validate_longitude
from apps.networks.models import Network
from common.exceptions import ValidationError
from common.pagination import DistanceCursorPagination
from common.permissions import IsMasterAgent, IsMinorAgent

NEARBY_DEFAULT_RADIUS_KM = 10
NEARBY_MAX_RADIUS_KM = 50


class MasterProfileView(RetrieveUpdateAPIView):
    serializer_class = MasterAgentProfileSerializer
    permission_classes = [IsAuthenticated, IsMasterAgent]

    def get_object(self):
        return MasterAgentProfile.objects.get(user=self.request.user)


class MinorProfileView(RetrieveUpdateAPIView):
    serializer_class = MinorAgentProfileSerializer
    permission_classes = [IsAuthenticated, IsMinorAgent]

    def get_object(self):
        return self.request.user.minor_profile


class NetworkStatusView(GenericAPIView):
    serializer_class = AgentNetworkStatusSerializer
    permission_classes = [IsAuthenticated, IsMasterAgent]

    def get(self, request, *args, **kwargs):
        profile = MasterAgentProfile.objects.get(user=request.user)
        statuses = list_network_statuses(profile)
        serializer = self.get_serializer(statuses, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = MasterAgentProfile.objects.get(user=request.user)
        network = Network.objects.get(pk=serializer.validated_data["network_id"])
        status_obj = set_network_status(
            profile, network, serializer.validated_data["is_active"]
        )
        result_serializer = self.get_serializer(status_obj)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class NearbyMasterAgentsView(ListAPIView):
    serializer_class = MasterAgentNearbySerializer
    permission_classes = [IsAuthenticated, IsMinorAgent]
    pagination_class = DistanceCursorPagination

    def list(self, request, *args, **kwargs):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        if lat is None or lng is None:
            raise ValidationError("lat and lng query parameters are required.")

        try:
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            raise ValidationError("lat and lng must be numeric values.") from None

        validate_latitude(lat)
        validate_longitude(lng)

        try:
            radius_km = float(
                request.query_params.get("radius_km", NEARBY_DEFAULT_RADIUS_KM)
            )
        except (TypeError, ValueError):
            raise ValidationError("radius_km must be a numeric value.") from None

        if radius_km <= 0 or radius_km > NEARBY_MAX_RADIUS_KM:
            raise ValidationError(
                f"radius_km must be between 1 and {NEARBY_MAX_RADIUS_KM}."
            )

        network_id = request.query_params.get("network")
        search_query = request.query_params.get("search")

        queryset = search_nearby_master_agents(
            point=(lat, lng),
            radius_km=radius_km,
            network_id=network_id,
            search_query=search_query,
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MasterAgentDetailView(RetrieveAPIView):
    queryset = MasterAgentProfile.objects.filter(is_active=True)
    serializer_class = MasterAgentProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
