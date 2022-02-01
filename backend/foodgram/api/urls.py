from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter

from .views import (APIGetToken, ChangePasswordView, RecipesViewSet,
                    TagsViewSet, IngredientsViewSet, UsersViewSet,
                    APISignup, SubscriptionsViewSet)

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
    'users/subscriptions',
    SubscriptionsViewSet,
    basename='subscriptions'
)
# router.register(
#     'users',
#     UsersViewSet,
#     basename='users'
# )

urlpatterns = [
    # path('auth/token/login/', APIGetToken.as_view(), name='get_token'),
    # path('users/set_password/', ChangePasswordView, name='set_password'),
    path('', include(router.urls)),
    # path('api-token-auth/', views.obtain_auth_token, name='auth_token'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    # path('api-token-auth/', views.obtain_auth_token, name='auth_token'),
    # path('auth/token/login/', APISignup.as_view(), name='signup')
]
