from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    """
    অনুমতি দেয় শুধুমাত্র admin (is_staff=True) ইউজারদের।
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsSuperUser(BasePermission):
    """
    অনুমতি দেয় শুধুমাত্র superuser (is_superuser=True) ইউজারদের।
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)

class IsAdminOrSuperUser(BasePermission):
    """
    অনুমতি দেয় যদি ইউজার admin বা superuser হয়।
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                request.user.is_staff or request.user.is_superuser
            )
        )

class IsOwnerOrReadOnly(BasePermission):
    """
    শুধুমাত্র owner edit/delete করতে পারবে, অন্যরা শুধু read করতে পারবে (GET, HEAD, OPTIONS)।
    """
    def has_object_permission(self, request, view, obj):
        # যদি শুধু read-method হয় (GET, HEAD, OPTIONS) তাহলে অনুমতি দেওয়া হবে
        if request.method in SAFE_METHODS:
            return True
        # শুধু owner কে write অনুমতি দেওয়া হবে
        return obj.owner == request.user

class IsAffiliateUser(BasePermission):
    """
    অনুমতি দেয় শুধুমাত্র affiliate টাইপ ইউজারদের। ধরুন আপনার ইউজার মডেলে user_type ফিল্ড আছে।
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'affiliate')

