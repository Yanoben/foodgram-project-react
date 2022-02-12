from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from api.filters import RecipeTagFilter
from .permissions import (AdminAuthorPermission, IsAdminUserOrReadOnly)
from app.models import FavoriteRecipes, Follow, ShoppingCart, Tags, Ingredients, Recipes
from .serializers import (SignupSerializer, GetTokenSerializer,
                          RetrieveRecipesSerializer, TagSerializer,
                          IngredientSerializer, UsersSerializer,
                          ChangePasswordSerializer, CreateRecipeSerializer,
                          RecipeFollowSerializer)
from django.conf import settings
from users.models import UserProfile
from rest_framework import generics
# from .pagination import CustomPagination


User = settings.AUTH_USER_MODEL


class TagsViewSet(ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    # pagination_class = CustomPagination
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = (IsAdminUserOrReadOnly,)
        return [permission() for permission in permission_classes]


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    # permission_classes = (IsAdminUserOrReadOnly,)
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeTagFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return CreateRecipeSerializer
        return RetrieveRecipesSerializer

    # def get_permissions(self):
    #     if self.action != 'create':
    #         return (AuthorOrReadOnly(),)
    #     return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'], )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        if request.method == 'POST':
            FavoriteRecipes.objects.create(user=request.user, recipes=recipe)
            data = RecipeFollowSerializer(recipe).data
            return Response(data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_obj(ShoppingCart, request.user, pk)
        return None

    # def get_object(self):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     return queryset

    def get_queryset(self):
        user = self.request.user
        queryset = Recipes.objects.all()
        tags = self.request.data.get('tags')
        if tags:
            queryset = queryset and Recipes.objects.filter(tags__slug__in=tags)
        if user.is_anonymous:
            return queryset
        try:
            recipe_id = self.kwargs['pk']
            return Recipes.objects.get(id=recipe_id)
        except KeyError:
            recipe_id = None
        author_id = self.request.data.get('author')
        if author_id:
            queryset = (
                queryset and Recipes.objects.filter(
                    author=get_object_or_404(User, id=author_id))
                    )

        if self.request.data.get('is_favorited') == 1:
            queryset = queryset and user.favorite_recipes.all()
        if self.request.data.get('is_in_shopping_cart') == 1:
            queryset = queryset and user.shopping_cart_recipes.all()
        return queryset


class APISignup(APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


class APIGetToken(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = UserProfile.objects.get(email=data['email'])
        except UserProfile.DoesNotExist:
            return Response({'username': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if data.get('password') == user.password:
            token = RefreshToken.for_user(user).access_token
            return Response({'auth_token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response({'Password': 'Wrong password!'},
                        status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UsersSerializer
    filter_backends = [SearchFilter, ]
    search_fields = ('username', )
    # pagination_class = CustomPagination

    def create(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = (AdminAuthorPermission, IsAuthenticated)
        return [permission() for permission in permission_classes]


class SubscriptionsViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    permission_classes = [AllowAny]


class ChangePasswordView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
