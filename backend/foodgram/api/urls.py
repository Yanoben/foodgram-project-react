from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter

from .views import (APIGetToken, APISignup, TagsViewSet, CommentsViewSet,
                    IngredientsViewSet, ReviewViewSet, RecipesViewSet,
                    UsersViewSet,)

router = SimpleRouter()

app_name = 'api'

router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')
router.register(r'users', UsersViewSet, basename='users')

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

urlpatterns = [
    path('auth/token/', APIGetToken.as_view(), name='get_token'),
    path('', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token, name='auth_token'),
    path('auth/signup/', APISignup.as_view(), name='signup'),
]
