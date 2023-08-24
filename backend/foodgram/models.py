from django.db import models
from django.db.models import UniqueConstraint

from users.models import CustomUser


class Tags(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10, null=True)
    slug = models.SlugField(
        max_length=200,
        null=True,
    )

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    measurement_unit = models.CharField(
        max_length=200, blank=False, null=False
    )


class Recipes(models.Model):
    ingredients = models.ManyToManyField(
        Ingredients,
        through="RecipesIngredients",
        through_fields=("recipes", "ingredients"),
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tags,
        through="RecipesTags",
    )
    image = models.ImageField(
        upload_to="recipes/images/", null=False, blank=False
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
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True)

    def __str__(self):
        return self.name

    def count_recipe(self):
        return Favorite.objects.filter(recipe=self).count()

    count_recipe.short_description = "count_recipe"

    class Meta:
        ordering = ["-pub_date"]


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        CustomUser,
        editable=True,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="following",
    )

    def __str__(self) -> str:
        return f"{self.user} {self.author}"


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user",
    )
    recipe = models.ForeignKey(
        Recipes,
        editable=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="favorite_recipe",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="constraints_user_recipe",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.recipe}"


class ShopingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="shoper",
    )
    recipe = models.ForeignKey(
        Recipes,
        editable=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="shopping_recipe",
    )


class RecipesIngredients(models.Model):
    recipes = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name="recipes_ingredients"
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name="recipes_ingredient",
    )
    amount = models.SmallIntegerField(blank=False, default=0)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["recipes", "ingredients"],
                name="constraints_recipes_ingredients",
            )
        ]


class RecipesTags(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recipe} {self.tag}"
