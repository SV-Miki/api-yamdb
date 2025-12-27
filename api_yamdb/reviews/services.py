from django.utils import timezone


def current_year() -> int:
    """Возвращает текущий год."""
    return timezone.now().year
