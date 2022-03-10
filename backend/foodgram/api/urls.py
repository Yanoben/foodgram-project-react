from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientsViewSet, RecipesViewSet, TagsViewSet,
                    UsersViewSet)

router = SimpleRouter()

app_name = 'api'

router.register(
    'tags',
    TagsViewSet,
    basename='tags'
)
router.register(
    'recipes',
    RecipesViewSet,
    basename='recipes'
)
router.register(
    'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)
router.register(
    'users',
    UsersViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
