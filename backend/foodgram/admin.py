from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    Tag,
    RecipeIngredient,
    RecipeTag,
    ShopingCart,
    Follow,
)


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

    @admin.display(description="count_recipe")
    def count_recipe(self, recipe):
        return Favorite.objects.filter(recipe=recipe).count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author").prefetch_related("tags", "ingredients")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")


@admin.register(Follow)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")


admin.site.register(Tag, RecipeIngredient, RecipeTag, ShopingCart)
