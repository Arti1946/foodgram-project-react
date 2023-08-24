import csv

from django.core.management.base import BaseCommand

from foodgram.models import Ingredients, Tags


def Ingredient(file: str) -> None:
    input_file = csv.DictReader(open(file, encoding="utf8"))
    for row in input_file:
        Ingredients.objects.create(
            name=row["name"], measurement_unit=row["unit"]
        )


def Tag(file: str) -> None:
    input_file = csv.DictReader(open(file, encoding="utf8"))
    for row in input_file:
        Tags.objects.create(
            name=row["name"], color=row["color"], slug=row["slug"]
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        Ingredient("data/ingredients.csv")
        Tag("data/tags.csv")
