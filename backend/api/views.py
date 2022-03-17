from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (IngredientSerializer, LowerRecipeSerializer,
                          ReadOnlyRecipeSerializer, RecipeSerializer,
                          TagSerializer,)
from .utility import create_txt


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyRecipeSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        return create_txt(request)


def add_recipe(model, user, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(user=user, recipe=recipe).exists():
        if model.__name__ == 'Favorite':
            return Response(
                {'errors': 'Рецепт уже есть в избранном.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif model.__name__ == 'ShoppingCart':
            return Response(
                {'errors': 'Рецепт уже есть в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        model.objects.create(user=user, recipe=recipe)
        serializer = LowerRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def del_recipe(model, user, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(user=user, recipe=recipe).exists():
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        if model.__name__ == 'Favorite':
            return Response(
                {'errors': 'Рецепта нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif model.__name__ == 'ShoppingCart':
            return Response(
                {'errors': 'Рецепта нет в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def favorite(request, pk):
    if request.method == 'POST':
        return add_recipe(Favorite, request.user, pk)
    elif request.method == 'DELETE':
        return del_recipe(Favorite, request.user, pk)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def shopping_cart(request, pk):
    if request.method == 'POST':
        return add_recipe(ShoppingCart, request.user, pk)
    elif request.method == 'DELETE':
        return del_recipe(ShoppingCart, request.user, pk)
