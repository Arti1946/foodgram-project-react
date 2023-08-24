import re

from django.core.exceptions import ValidationError


def validate_username(value):
    regex = re.compile(r"^[\w.@+-]+\Z")
    if not regex.match(value):
        raise ValidationError("Выберите другое имя")
    elif value == "me":
        raise ValidationError("Нельзя выбрать такое имя")
