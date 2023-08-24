import re

from django.core.exceptions import ValidationError


def validate_slug(value):
    regex = re.compile(r"^[-a-zA-Z0-9_]+$")
    if not regex.match(value):
        raise ValidationError("Выберите другой slug")
