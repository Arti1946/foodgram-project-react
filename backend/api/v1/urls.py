from rest_framework import routers

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import (
    IngredientViewSet, RecipeViewSet, TagsViewSet, UserViewSet, subscribe,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"recipes", RecipeViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"tags", TagsViewSet)

urlpatterns = [
    path("users/<int:pk>/subscribe/", subscribe),
    path("", include(router.urls)),
    path("api/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
