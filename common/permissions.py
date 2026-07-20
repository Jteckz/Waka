from rest_framework.permissions import SAFE_METHODS, BasePermission

from common.constants import RoleChoices


class IsMasterAgent(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == RoleChoices.MASTER_AGENT


class IsMinorAgent(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == RoleChoices.MINOR_AGENT


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == RoleChoices.ADMIN


class IsOwnerOrReadOnly(BasePermission):
    owner_field = "user"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, self.owner_field, None)
        return owner is not None and owner == request.user
