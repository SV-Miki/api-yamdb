from django.core.exceptions import ValidationError

from api_yamdb.constants import RESERVED_USERNAME


def validate_username_not_reserved(value: str) -> None:
    """Запрещает использование зарезервированного username."""

    if value == RESERVED_USERNAME:
        raise ValidationError(
            f'Нельзя использовать username "{RESERVED_USERNAME}".'
        )
