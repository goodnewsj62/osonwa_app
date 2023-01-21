from rest_framework.permissions import BasePermission, SAFE_METHODS


class LockOut(BasePermission):
    """
    Block Out All Users
    """

    message = "Permission Denied"

    def has_permission(self, request, view):
        return False


class IsUserAccount(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user


class PermitSafeAccess(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user and request.user.is_active
