from rest_framework.permissions import BasePermission

class IsEmailVerified(BasePermission):
    """
    Разрешает доступ только подтверждённым пользователям
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)
