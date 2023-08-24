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
    def count_recipe(self):
        return Favorite.objects.filter(recipe=self).count()

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

    def get_queryset(self, request):
        Recipe.object.select_related("author").prefetch_related(
            "ingredients", "tags"
        ).all()


admin.site.register(Tag)
