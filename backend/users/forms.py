from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """form to create user."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email", "password")


class CustomUserChangeForm(UserChangeForm):
    """Form, to change user info."""

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email", "password")
