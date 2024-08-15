from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or staff to edit or delete user profiles.
    Regular users can only read their profiles.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
