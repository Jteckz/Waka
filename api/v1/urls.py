from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.api.v1.urls")),
    path("", include("apps.networks.api.v1.urls")),
    path("agents/", include("apps.agents.api.v1.urls")),
]
