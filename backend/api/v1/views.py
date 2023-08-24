from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from foodgram.models import (
    CustomUser, Favorite, Follow, Ingredients, Recipes, RecipesIngredients,
    ShopingCart, Tags,
)

from .filters import IngredientsFilter, RecipeFilter
from .serializers import (
    CustomUserSerializer, FavoriteRecipeSerializer, FollowSerializer,
    FollowSerializerPost, IngredientsSerializer, RecipeSerializer,
    RecipeSerializerPost, ShopingCartSerializer, TagsSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    class Meta:
        ordering = ["-id"]

    def get_queryset(self):
        query = (
            Recipes.objects.select_related("author")
            .prefetch_related("ingredients", "tags")
            .all()
        )
        return query

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return RecipeSerializer
        return RecipeSerializerPost

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        user = request.user
        if request.method == "POST":
            if not Favorite.objects.filter(user=user, recipe=pk).exists():
                recipe = get_object_or_404(Recipes, pk=pk)
                serializer = FavoriteRecipeSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                "Рецепт уже в избранном", status=status.HTTP_400_BAD_REQUEST
            )
        if not Favorite.objects.filter(user=user, recipe=pk).delete():
            return Response(
                "Рецепта нет в избранном", status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            "Рецепт удален из избранного", status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        user = request.user
        if not user.is_authenticated:
            return Response(
                "Вы не авторизованы", status=status.HTTP_401_UNAUTHORIZED
            )
        if request.method == "POST":
            if not ShopingCart.objects.filter(user=user, recipe=pk).exists():
                recipe = get_object_or_404(Recipes, pk=pk)
                serializer = ShopingCartSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                "Рецепт уже в корзине", status=status.HTTP_400_BAD_REQUEST
            )
        if not ShopingCart.objects.filter(user=user, recipe=pk).delete():
            return Response(
                "Рецепта нет в корзине", status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            "Рецепт удален из корзины", status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shop_list = []
        user = get_object_or_404(CustomUser, username=request.user)
        ingredients = (
            RecipesIngredients.objects.filter(
                recipes__shopping_recipe__user=user
            )
            .values("ingredients__name", "ingredients__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        return self.create_shoping_list(self, ingredients, shop_list)

    def create_shoping_list(self, ingredients, shop_list: list):
        for ingredient in ingredients:
            shop_list.append(
                "{name}({measurement_unit}) - {amount}\n".format(
                    name=object.get("ingredients__name"),
                    measurement_unit=object.get(
                        "ingredients__measurement_unit"
                    ),
                    amount=object.get("amount"),
                )
            )
        response = FileResponse(shop_list, content_type="text/plain")
        return response


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    http_method_names = ["get", "post"]
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        serializer = SetPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.data["new_password"])
        return Response("вы изменили свой пароль", status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        follow = Follow.objects.filter(user=user)
        page = self.paginate_queryset(follow)
        serializer = FollowSerializer(
            page, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)


class SubscribeApiView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["post", "delete"]

    def post(self, request, pk):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)
        query = Follow.objects.filter(user=user, author=pk).annotate(
            recipes_count=Count("author__recipe")
        )
        if user == author:
            return Response(
                "Нельзя подписаться на себя",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not Follow.objects.filter(user=user, author=pk).exists():
            serializer = FollowSerializerPost(
                instance=query,
                data=request.data,
                context={"request": request},
            )
            if serializer.is_valid():
                serializer.save(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            "Вы уже подписаны на этого пользователя",
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)
        if not Follow.objects.filter(user=user, author=pk).delete():
            return Response(
                "Вы не подписаны на этого пользователя",
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            f"Вы отписались от автора {author.username}",
            status=status.HTTP_204_NO_CONTENT,
        )


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter


class TagsViewSet(viewsets.ModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tags.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination