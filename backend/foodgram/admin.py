from django.contrib import admin

from .models import (
    Favorite, Follow, Ingredient, Recipe, RecipeIngredient, ShopingCart, Tag,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "count_recipe",
    )
    list_filter = ("author", "tags")
    search_fields = ("name",)
    empty_value_display = "-пусто-"

    @admin.display(description="count_recipe")
    def count_recipe(self, recipe):
        return Favorite.objects.filter(recipe=recipe).count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author").prefetch_related(
            "tags", "ingredients"
        )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author", "user")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("recipe", "user")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    search_fields = ("name", "slug")
    empty_value_display = "-пусто-"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "ingredients",
        "recipes",
        "amount",
    )
    search_fields = ("ingredients", "recipes")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("ingredients", "recipes")


@admin.register(ShopingCart)
class ShopingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user", "recipe")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("recipe", "user")
