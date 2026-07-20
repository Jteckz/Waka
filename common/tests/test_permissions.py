import pytest
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.accounts.tests.factories import UserFactory
from common.constants import RoleChoices
from common.permissions import (
    IsAdminRole,
    IsMasterAgent,
    IsMinorAgent,
    IsOwnerOrReadOnly,
)

factory = APIRequestFactory()


class _ProtectedView(APIView):
    permission_classes = []

    def get(self, request):
        return Response("ok")


@pytest.mark.parametrize(
    ("permission_class", "role", "expected"),
    [
        (IsMasterAgent, RoleChoices.MASTER_AGENT, True),
        (IsMasterAgent, RoleChoices.MINOR_AGENT, False),
        (IsMasterAgent, RoleChoices.ADMIN, False),
        (IsMinorAgent, RoleChoices.MASTER_AGENT, False),
        (IsMinorAgent, RoleChoices.MINOR_AGENT, True),
        (IsMinorAgent, RoleChoices.ADMIN, False),
        (IsAdminRole, RoleChoices.MASTER_AGENT, False),
        (IsAdminRole, RoleChoices.MINOR_AGENT, False),
        (IsAdminRole, RoleChoices.ADMIN, True),
    ],
)
@pytest.mark.django_db
def test_role_permissions(permission_class, role, expected):
    user = UserFactory(role=role)
    request = factory.get("/")
    force_authenticate(request, user=user)
    view = _ProtectedView.as_view(permission_classes=[permission_class])
    response = view(request)
    assert (response.status_code == 200) is expected


@pytest.mark.django_db
def test_denies_anonymous():
    request = factory.get("/")
    view = _ProtectedView.as_view(permission_classes=[IsMasterAgent])
    response = view(request)
    assert response.status_code == 401


class TestIsOwnerOrReadOnly:
    def test_allows_read_for_non_owner(self):
        obj = type("Obj", (), {"user": type("U", (), {"pk": 2})()})()
        request = factory.get("/")
        request.user = type("U", (), {"pk": 1})()
        assert IsOwnerOrReadOnly().has_object_permission(request, None, obj) is True

    def test_allows_read_for_owner(self):
        user = type("U", (), {"pk": 1})()
        obj = type("Obj", (), {"user": user})()
        request = factory.get("/")
        request.user = user
        assert IsOwnerOrReadOnly().has_object_permission(request, None, obj) is True

    def test_allows_write_for_owner(self):
        user = type("U", (), {"pk": 1})()
        obj = type("Obj", (), {"user": user})()
        request = factory.post("/")
        request.user = user
        assert IsOwnerOrReadOnly().has_object_permission(request, None, obj) is True

    def test_denies_write_for_non_owner(self):
        obj = type("Obj", (), {"user": type("U", (), {"pk": 2})()})()
        request = factory.put("/")
        request.user = type("U", (), {"pk": 1})()
        assert IsOwnerOrReadOnly().has_object_permission(request, None, obj) is False

    def test_safe_methods_allowed_for_anyone(self):
        obj = type("Obj", (), {"user": type("U", (), {"pk": 2})()})()
        for method in SAFE_METHODS:
            request = getattr(factory, method.lower())("/")
            request.user = type("U", (), {"pk": 1})()
            assert IsOwnerOrReadOnly().has_object_permission(request, None, obj) is True

    def test_custom_owner_field(self):
        perm = IsOwnerOrReadOnly()
        perm.owner_field = "created_by"
        user = type("U", (), {"pk": 1})()
        obj = type("Obj", (), {"created_by": user})()
        request = factory.delete("/")
        request.user = user
        assert perm.has_object_permission(request, None, obj) is True

    def test_denies_write_when_no_owner_attribute(self):
        obj = type("Obj", (), {})()
        request = factory.patch("/")
        request.user = type("U", (), {"pk": 1})()
        assert IsOwnerOrReadOnly().has_object_permission(request, None, obj) is False
