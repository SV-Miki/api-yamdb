from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api_yamdb.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from users.validators import validate_username_not_reserved


validate_username_not_me = validate_username_not_reserved


class User(AbstractUser):
    """Кастомный пользователь YaMDb."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLE_CHOICES = (
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    )

    ROLE_MAX_LENGTH = max(len(role) for role, _ in ROLE_CHOICES)

    username = models.CharField(
        "username",
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username_not_reserved,
        ],
    )

    email = models.EmailField(
        "email", max_length=EMAIL_MAX_LENGTH, unique=True
    )
    bio = models.TextField("bio", blank=True)
    role = models.CharField(
        "role",
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
    )

    REQUIRED_FIELDS = ("email",)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

    @property
    def is_admin(self) -> bool:
        return bool(self.is_superuser or self.role == self.ADMIN)

    @property
    def is_moderator(self) -> bool:
        return self.role == self.MODERATOR
