from rest_framework import routers

from django.urls import include, path

from .views import (
    DownloadShopCartView, IngredientViewSet, RecipeViewSet, SubscribeApiView,
    SubscriptionsApiView, TagsViewSet,
)

router = routers.DefaultRouter()
router.register(r"recipes", RecipeViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"tags", TagsViewSet)

urlpatterns = [
    path("users/<int:pk>/subscribe/", SubscribeApiView.as_view()),
    path("users/subscriptions/", SubscriptionsApiView.as_view()),
    path("recipes/download_shopping_cart/", DownloadShopCartView.as_view()),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
