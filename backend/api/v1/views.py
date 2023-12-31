import io

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from foodgram.models import (
    CustomUser, Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
    ShopingCart, Tag,
)

from .filters import IngredientsFilter, RecipeFilter
from .serializers import (
    FavoriteRecipeSerializer, FollowSerializer, FollowSerializerPost,
    IngredientsSerializer, RecipeSerializer, RecipeSerializerPost,
    ShopingCartSerializer, TagsSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    class Meta:
        ordering = ["-id"]

    def get_queryset(self):
        query = Recipe.objects.select_related("author").prefetch_related(
            "ingredients", "tags"
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
                recipe = get_object_or_404(Recipe, pk=pk)
                serializer = FavoriteRecipeSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                "Рецепт уже в избранном", status=status.HTTP_400_BAD_REQUEST
            )
        if Favorite.objects.filter(user=user, recipe=pk).delete()[0] == 0:
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
                recipe = get_object_or_404(Recipe, pk=pk)
                serializer = ShopingCartSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                "Рецепт уже в корзине", status=status.HTTP_400_BAD_REQUEST
            )
        if ShopingCart.objects.filter(user=user, recipe=pk).delete()[0] == 0:
            return Response(
                "Рецепта нет в корзине", status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            "Рецепт удален из корзины", status=status.HTTP_204_NO_CONTENT
        )


class DownloadShopCartView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]
    pagination_class = None

    def get(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(
                recipes__shopping_recipe__user=user
            )
            .values("ingredients__name", "ingredients__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        buffer_data = self.write_to_buffer(ingredients=ingredients)
        response = HttpResponse(buffer_data, content_type="StringIO/plain")
        return response

    def write_to_buffer(self, ingredients):
        in_memory = io.StringIO()
        for ingredient in ingredients:
            in_memory.write(
                "{name}({measurement_unit}) - {amount}\n".format(
                    name=ingredient.get("ingredients__name"),
                    measurement_unit=ingredient.get(
                        "ingredients__measurement_unit"
                    ),
                    amount=ingredient.get("amount"),
                )
            )
        return in_memory.getvalue()


class SubscriptionsApiView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request):
        user = request.user
        follow = Follow.objects.filter(user=user).annotate(
            recipes_count=Count("author__recipe")
        )
        page = self.paginate_queryset(follow, request, view=self)
        serializer = FollowSerializer(
            page, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)


class SubscribeApiView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["post", "delete"]
    pagination_class = None

    def post(self, request, pk):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)
        if user == author:
            return Response(
                "Нельзя подписаться на себя",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not Follow.objects.filter(user=user, author=author).exists():
            Follow.objects.create(user=user, author=author)
            query = Follow.objects.filter(user=user).annotate(
                recipes_count=Count("author__recipe")
            )
            serializer = FollowSerializerPost(
                query, context={"request": request}, many=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            "Вы уже подписаны на этого пользователя",
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        user = request.user
        if Follow.objects.filter(user=user, author=pk).delete()[0] == 0:
            return Response(
                "Вы не подписаны на этого пользователя",
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            "Вы отписались от автора",
            status=status.HTTP_204_NO_CONTENT,
        )


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    http_method_names = ["get"]
    pagination_class = None

    class Meta:
        ordering = ["name"]


class TagsViewSet(viewsets.ModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get"]
    pagination_class = None

    class Meta:
        ordering = ["id"]
