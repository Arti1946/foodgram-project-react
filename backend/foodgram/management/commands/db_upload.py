import csv

from django.core.management.base import BaseCommand

from foodgram.models import Ingredients, Tags


def upload_ingredients(file: str) -> None:
    input_file = csv.DictReader(open(file, encoding="utf8"))
    for row in input_file:
        Ingredients.objects.create(
            name=row["name"], measurement_unit=row["unit"]
        )


def upload_tags(file: str) -> None:
    input_file = csv.DictReader(open(file, encoding="utf8"))
    for row in input_file:
        Tags.objects.create(
            name=row["name"], color=row["color"], slug=row["slug"]
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        upload_ingredients("data/ingredients.csv")
        upload_tags("data/tags.csv")
