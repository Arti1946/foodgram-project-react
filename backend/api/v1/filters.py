from django_filters import rest_framework as filters

from foodgram.models import Ingredient, Recipe, Tag


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="startswith", field_name="name")

    class Meta:
        fields = ("name", "measurement_unit", "id")
        model = Ingredient


class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter()
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        label="Tags",
        to_field_name="slug",
    )
    is_favorited = filters.BooleanFilter(method="get_favorite")
    is_in_shopping_cart = filters.BooleanFilter(method="get_is_in_shopp_cart")

    def get_favorite(self, queryset, value, name):
        if value:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopp_cart(self, queryset, value, name):
        if value:
            return queryset.filter(shopping_recipe__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")
