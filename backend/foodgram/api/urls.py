from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter

from .views import (APIGetToken, APISignup, RecipesViewSet,
                    TagsViewSet, IngredientsViewSet, UsersViewSet)

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
    path('auth/token/', APIGetToken.as_view(), name='get_token'),
    path('', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token, name='auth_token'),
    path('auth/signup/', APISignup.as_view(), name='signup'),
]
