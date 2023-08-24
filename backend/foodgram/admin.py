from django.contrib import admin

from .models import Favorite, Ingredients, Recipes, Tags


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
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
        Recipes.object.select_related("author").prefetch_related(
            "ingredients", "tags"
        ).all()

    def get_count_recipe(self):
        return Favorite.objects.filter(recipe=self).count()


admin.site.register(Tags)
