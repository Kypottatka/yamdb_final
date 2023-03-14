from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверка, что пользователь является администратором."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(permissions.BasePermission):
    """Проверка, что пользователь является модератором."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator


class ReadOnly(permissions.BasePermission):
    """Доступ только на чтение."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthor(permissions.BasePermission):
    """Проверка, что пользователь является автором."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """
    Проверка, что пользователь является админом, автором или модератором.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )


AdminOrReadOnly = IsAdmin | ReadOnly
