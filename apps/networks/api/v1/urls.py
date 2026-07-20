from django.urls import path

from apps.networks.api.v1 import views

urlpatterns = [
    path("networks/", views.NetworkListView.as_view(), name="network-list"),
]
