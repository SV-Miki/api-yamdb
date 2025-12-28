from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAuthenticatedOrReadOnly,
)


def _is_admin(user) -> bool:
    """Проверяет, является ли пользователь админом (role/staff/superuser)."""

    return bool(
        user and user.is_authenticated and getattr(user, "is_admin", False)
    )


class IsAdmin(BasePermission):
    """Доступ только для администратора."""

    def has_permission(self, request, view):
        return _is_admin(request.user)


class IsAdminOrReadOnly(BasePermission):
    """Чтение доступно всем, изменения - только администратору."""

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or _is_admin(request.user))


class IsAuthorModeratorAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Чтение доступно всем.

    Создание: только аутентифицированным.
    Изменение/удаление: автор или moderator/admin.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(
            request.method in SAFE_METHODS
            or (user and user.is_authenticated and (
                getattr(user, "is_admin", False)
                or getattr(user, "is_moderator", False)
                or obj.author_id == user.id
            ))
        )
