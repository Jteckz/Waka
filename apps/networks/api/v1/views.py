from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.networks.api.v1.serializers import NetworkSerializer
from apps.networks.models import Network


class NetworkListView(ListAPIView):
    queryset = Network.objects.filter(is_active=True)
    serializer_class = NetworkSerializer
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
