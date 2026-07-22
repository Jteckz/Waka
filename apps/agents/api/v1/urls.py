from django.urls import path

from apps.agents.api.v1 import views

urlpatterns = [
    path("master/me", views.MasterProfileView.as_view(), name="master-profile"),
    path("master/nearby", views.NearbyMasterAgentsView.as_view(), name="master-nearby"),
    path(
        "master/<uuid:pk>",
        views.MasterAgentDetailView.as_view(),
        name="master-detail",
    ),
    path("minor/me", views.MinorProfileView.as_view(), name="minor-profile"),
    path(
        "master/network-status",
        views.NetworkStatusView.as_view(),
        name="network-status",
    ),
]
