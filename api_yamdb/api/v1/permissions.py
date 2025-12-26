from rest_framework.permissions import SAFE_METHODS, BasePermission


def _is_admin(user) -> bool:
    """Проверяет, является ли пользователь админом

    (role=admin или superuser).
    """
    if not user or not user.is_authenticated:
        return False
    # суперпользователь всегда админ
    if getattr(user, "is_superuser", False):
        return True
    # кастомная роль
    return getattr(user, "role", None) == "admin"


class IsAdmin(BasePermission):
    """Доступ только для администратора (role=admin или superuser)."""

    def has_permission(self, request, view):
        return _is_admin(request.user)


class IsAdminOrReadOnly(BasePermission):
    """Чтение доступно всем, изменения - только администратору."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _is_admin(request.user)


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    """Чтение доступно всем.

    Создание/изменение/удаление: автор объекта
    или пользователь с ролью moderator/admin/superuser.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        # суперпользователь всегда может
        if getattr(user, "is_superuser", False):
            return True

        # роли
        role = getattr(user, "role", None)
        if role in ("admin", "moderator"):
            return True

        # автор
        return getattr(obj, "author_id", None) == user.id
