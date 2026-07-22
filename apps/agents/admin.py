from django.contrib import admin

from apps.agents.models import AgentNetworkStatus, MasterAgentProfile, MinorAgentProfile


@admin.register(MasterAgentProfile)
class MasterAgentProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "is_active", "response_rate")
    list_filter = ("is_active",)
    search_fields = ("business_name", "user__phone")


@admin.register(MinorAgentProfile)
class MinorAgentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name")
    search_fields = ("user__phone", "display_name")


@admin.register(AgentNetworkStatus)
class AgentNetworkStatusAdmin(admin.ModelAdmin):
    list_display = ("master_agent", "network", "is_active")
    list_filter = ("is_active", "network")
