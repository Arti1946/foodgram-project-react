import base64

import webcolors
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from foodgram.models import (
    CustomUser, Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
    RecipeTag, ShopingCart, Tag,
)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")
        return data


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("name", "id", "measurement_unit")


class ResIngSerializator(serializers.ModelSerializer):
    amount = serializers.IntegerField(source="recipes_ingredients__amount")

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipesIngredientsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="ingredients.name")
    measurement_unit = serializers.CharField(
        source="ingredients.measurement_unit"
    )
    id = serializers.IntegerField(source="ingredients.id")

    class Meta:
        fields = ("id", "name", "measurement_unit", "amount")
        model = RecipeIngredient


class TagsSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        fields = ("name", "id", "color", "slug")
        model = Tag


class TagRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id",)
        model = Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class RecipeSerializerPost(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    image = Base64ImageField(required=True)
    ingredients = serializers.ListField()
    tags = serializers.ListField()

    class Meta:
        fields = (
            "id",
            "name",
            "author",
            "image",
            "ingredients",
            "tags",
            "text",
            "cooking_time",
        )
        model = Recipe

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            amount = ingredient.pop("amount")
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient["id"]
            )
            RecipeIngredient.objects.create(
                ingredients=current_ingredient, recipes=recipe, amount=amount
            )
        for tag in tags:
            current_tag = get_object_or_404(Tag, id=tag)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        return recipe

    def to_representation(self, recipe):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeSerializer(recipe, context=context).data

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient.pop("amount")
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient["id"]
            )
            RecipeIngredient.objects.create(
                ingredients=current_ingredient, recipes=instance, amount=amount
            )
        instance.save()
        return instance


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "id",
        )
        model = CustomUser

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is not None:
            user = request.user
            if user.is_anonymous:
                return False
            return Follow.objects.filter(author=obj, user=user).exists()
        return False


class CustomUserPostSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "id",
            "password",
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipesIngredientsSerializer(
        many=True, source="recipes_ingredients"
    )
    tags = TagsSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "name",
            "author",
            "image",
            "ingredients",
            "tags",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return ShopingCart.objects.filter(
            recipe=obj, user=request.user
        ).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="recipe.name", read_only=True)
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    image = serializers.CharField(source="recipe.image", read_only=True)

    class Meta:
        model = Favorite
        fields = (
            "image",
            "cooking_time",
            "name",
            "id",
        )


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializerPost(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        fields = ("user", "author")
        model = Follow

    def to_representation(self, follow):
        request = self.context.get("request")
        context = {"request": request}
        return FollowSerializer(follow, context=context).data


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="author.email")
    id = serializers.IntegerField(source="author.id")
    username = serializers.CharField(source="author.username")
    first_name = serializers.CharField(source="author.first_name")
    last_name = serializers.CharField(source="author.last_name")
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta:
        model = Follow
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        user = request.user
        author = obj.author
        if Follow.objects.filter(user=user, author=author).exists:
            return True
        return False

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = None
        recipes = obj.author.recipe.all()[:limit]
        serializer = FollowRecipeSerializer(
            recipes, many=True, context=self.context
        )
        return serializer.data


class ShopingCartSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="recipe.name", read_only=True)
    cooking_time = serializers.CharField(
        source="recipe.cooking_time", read_only=True
    )
    image = serializers.CharField(source="recipe.image", read_only=True)
    id = serializers.IntegerField(source="recipe.id", read_only=True)

    class Meta:
        model = ShopingCart
        fields = ("name", "cooking_time", "image", "id")
