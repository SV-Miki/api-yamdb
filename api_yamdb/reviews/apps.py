from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Конфигурация Django-приложения reviews

    (каталог, отзывы и комментарии).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "reviews"
