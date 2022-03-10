from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken


from api.filters import IngredientsFilter, RecipeTagFilter
from app.models import (Favorite, Follow, Ingredient, Recipe,
                        RecipeIngredient, ShoppingCart, Tag)
from users.models import UserProfile
from .permissions import IsAdminUserOrReadOnly
from .serializers import (ChangePasswordSerializer, CreateRecipeSerializer,
                          GetTokenSerializer, IngredientSerializer,
                          RecipeFollowSerializer, RetrieveRecipesSerializer,
                          SignupSerializer, TagSerializer, UsersSerializer)

User = settings.AUTH_USER_MODEL


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = (IsAdminUserOrReadOnly,)
        return [permission() for permission in permission_classes]


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeTagFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RetrieveRecipesSerializer

    @action(detail=True, methods=['post', 'delete'], )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            Favorite.objects.create(user=request.user, recipe=recipe)
            data = RecipeFollowSerializer(recipe).data
            return Response(data)
        if request.method == 'DELETE':
            return self.delete_obj(Follow, request.user, pk)

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.get(pk=pk)
        if request.method == 'GET':
            return ShoppingCart.objects.create(
                user=request.user, recipe=recipe)
        if request.method == 'DELETE':
            return self.delete_obj(ShoppingCart, request.user, pk)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__user=request.user).values(
            'ingredients__name',
            'ingredients__measurement_unit').annotate(total=sum('amount'))
        shopping_list = 'Список покупок:\n\n'
        for number, ingredient in enumerate(ingredients, start=1):
            shopping_list += (
                f'{ingredient["ingredients__name"]}: '
                f'{ingredient["total"]} '
                f'{ingredient["ingredients__measurement_unit"]}\n')

        cart = 'shopping-list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (f'attachment;'
                                           f'filename={cart}')
        return response


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
    lookup_field = 'id'

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if self.request.method == 'GET':
            data = UsersSerializer(self.request.user).data
            return Response(data)

    @action(detail=False, methods=['get', 'post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(UserProfile, id=id)
        if self.request.method == 'POST':
            if request.user != author:
                Follow.objects.create(user=request.user, author=author)
                data = UsersSerializer(author).data
                return Response(data)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        return Response(queryset)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
