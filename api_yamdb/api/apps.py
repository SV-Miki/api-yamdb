from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфигурация Django-приложения api (роутинг и версия v1)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
