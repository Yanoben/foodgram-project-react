from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet, favorite,
                    shopping_cart,)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:pk>/favorite/', favorite, name='favorite'),
    path(
        'recipes/<int:pk>/shopping_cart/', shopping_cart, name='shopping_cart'
    ),
]
