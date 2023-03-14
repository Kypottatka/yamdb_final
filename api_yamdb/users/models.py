from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validators import username_validator

USER = "user"
MODERATOR = "moderator"
ADMIN = "admin"

ROLES = [
    (USER, "Пользователь"),
    (MODERATOR, "Модератор"),
    (ADMIN, "Администратор"),
]


class User(AbstractUser):
    username = models.CharField(
        verbose_name="Никнейм пользователя",
        max_length=settings.USER_FIELD_LENGTH,
        unique=True,
        validators=[username_validator, UnicodeUsernameValidator()],
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=settings.USER_FIELD_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=settings.USER_FIELD_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=settings.USER_FIELD_LENGTH,
        blank=True,
    )
    role = models.CharField(
        verbose_name="Роль",
        max_length=settings.USER_FIELD_LENGTH,
        choices=ROLES,
        default=USER,
    )
    bio = models.TextField(
        verbose_name="О себе",
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def is_moderator(self):
        return self.is_staff or self.role == MODERATOR

    @property
    def is_admin(self):
        return self.is_superuser or self.role == ADMIN

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_username_email"
            )
        ]

    def __str__(self) -> str:
        return self.username
