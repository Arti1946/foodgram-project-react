from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validatorsr import validate_username


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(
        max_length=150, unique=True, validators=[validate_username]
    )
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    password = models.CharField(max_length=150, blank=False, null=False)
    is_subscribed = models.BooleanField(default="False")
