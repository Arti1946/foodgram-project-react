from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    @admin.display(description="count_recipe")
    def count_recipe(self, recipe):
        return Favorite.objects.filter(recipe=recipe).count()

    list_display = (
        "name",
        "author",
        "count_recipe",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-пусто-"


admin.site.register(Tag)
