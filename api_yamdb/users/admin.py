from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-конфигурация кастомной модели User для YaMDb.

    Добавляет в админку поля роли и био,
    а также выводит расширенный список колонок.
    """

    fieldsets = UserAdmin.fieldsets + (("YaMDb", {"fields": ("role", "bio")}),)
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
