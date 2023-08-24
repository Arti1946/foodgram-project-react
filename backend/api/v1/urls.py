from rest_framework import routers

from django.urls import include, path

from .views import (
    IngredientViewSet, RecipeViewSet, SubscribeApiView, TagsViewSet,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"recipes", RecipeViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"tags", TagsViewSet)

urlpatterns = [
    path("users/<int:pk>/subscribe/", SubscribeApiView.as_view()),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]