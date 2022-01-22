from rest_framework import permissions


class DeskPermission(permissions.BasePermission):
    """
    Ensure that the user is authenticated and assigned to a desk
    """
    def has_permission(self, request, view):
        return (
            request.user.is_superuser or
            request.desk is not None
        )


class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_superuser or
            request.user.permissions.is_admin
        )


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_superuser or
            request.method in permissions.SAFE_METHODS or
            request.user.permissions.is_admin
        )


class IsOrganizationAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_superuser or
            request.user.permissions.is_organization_admin
        )