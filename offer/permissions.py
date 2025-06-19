from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission:
    - Admin users (is_staff=True) can perform any action.
    - Non-admin users can only perform safe (read-only) methods: GET, HEAD, OPTIONS.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            (request.user and request.user.is_staff)
        )