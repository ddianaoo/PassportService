from rest_framework import permissions


class IsClient(permissions.BasePermission):
    """
    Custom permission to only allow access to users who are not staff or admin.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser
