from django.contrib import admin

from .models import Ingredients, Recipes, Tags


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-пусто-"


RecipeAdmin.list_display += ("count_recipe",)
admin.site.register(Ingredients, IngredientAdmin)
admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Tags)
