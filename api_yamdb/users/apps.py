from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация Django-приложения users

    (кастомная модель пользователя YaMDb).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "Пользователи"
