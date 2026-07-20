from django.contrib import admin

from apps.networks.models import Network


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ("name", "network_type", "is_active")
    list_filter = ("network_type",)
