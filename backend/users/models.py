from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class CustomUser(AbstractUser):
    email = models.EmailField("Почта", unique=True, max_length=254)
    username = models.CharField(
        max_length=150, unique=True, validators=[validate_username]
    )
    first_name = models.CharField(
        "Имя", max_length=150, blank=False, null=False
    )
    last_name = models.CharField(
        "Фамилия", max_length=150, blank=False, null=False
    )
    password = models.CharField(
        "Пароль", max_length=150, blank=False, null=False
    )
    is_subscribed = models.BooleanField("Оформлена подписка", default="False")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username
