from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


def validate_username_not_me(value: str) -> None:
    """Запрещает использование зарезервированного username='me'."""
    if value.lower() == "me":
        raise ValidationError('Нельзя использовать username "me".')


class User(AbstractUser):
    """Кастомный пользователь YaMDb.

    Расширяет AbstractUser:
    - добавляет поля role и bio
    - делает email уникальным
    - вводит роли (user/moderator/admin)
    и удобные свойства is_admin/is_moderator
    """

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLE_CHOICES = (
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    )

    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username_not_me],
    )

    email = models.EmailField("email", unique=True)
    bio = models.TextField("bio", blank=True)
    role = models.CharField(
        "role", max_length=16, choices=ROLE_CHOICES, default=USER
    )

    REQUIRED_FIELDS = ("email",)

    @property
    def is_admin(self) -> bool:
        return self.is_superuser or self.role == self.ADMIN

    @property
    def is_moderator(self) -> bool:
        return self.role == self.MODERATOR

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
