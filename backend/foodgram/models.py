from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField("Название", max_length=200)
    color = models.CharField("Цвет", max_length=10)
    slug = models.SlugField(
        "Слаг",
        max_length=200,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        "Название", max_length=200, blank=False, null=False
    )
    measurement_unit = models.CharField(
        "Единица измерения", max_length=200, blank=False, null=False
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        through_fields=("recipes", "ingredients"),
        related_name="recipes",
        verbose_name="Ингредиент",
    )
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
        verbose_name="Тег",
        related_name="recipes",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        null=False,
        blank=False,
        verbose_name="Изображение",
    )
    name = models.CharField(
        "Название",
        max_length=200,
        blank=False,
        null=False,
    )
    text = models.TextField("Описание", blank=False, null=False)
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления(в минутах)",
        blank=False,
        null=False,
        validators=[MinValueValidator(1, "Это слишком быстро")],
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        CustomUser,
        editable=True,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self) -> str:
        return f"{self.user} {self.author}"


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        editable=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="favorite_recipe",
        verbose_name="Рецепт",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe",
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self) -> str:
        return {self.recipe}


class ShopingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="shoper",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        editable=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="shopping_recipe",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return self.recipe


class RecipeIngredient(models.Model):
    recipes = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipes_ingredients"
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipes_ingredients",
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        validators=[MinValueValidator(1, "Слишком малое количество")],
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["recipes", "ingredients"],
                name="unique_recipes_ingredients",
            )
        ]
        verbose_name = "Рецепт и ингредиент"
        verbose_name_plural = "Рецепты и ингредиенты"


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_tags"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="recipe_tags"
    )

    class Meta:
        verbose_name = "Рецепт и Тег"
        verbose_name_plural = "Рецепты и Теги"

    def __str__(self):
        return self.recipe
