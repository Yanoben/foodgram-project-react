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
    pagination_class = None
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
    # filterset_class = RecipeTagFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
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

    # @action(detail=False)
    # def download_shopping_cart(self, request):
    #     shop_list = list(
    #         request.user.user_shopping_list.values_list('recipe__components'))
    #     for item in range(0, len(shop_list)):
    #         shop_list[item] = shop_list[item][0]
    #     ingredients_in_recipes = Amount.objects.in_bulk(shop_list)
    #     shop_dictary = {}
    #     for obj in ingredients_in_recipes.values():
    #         ingredient = obj.ingredient
    #         amount = obj.amount
    #         if ingredient.id in shop_dictary:
    #             shop_dictary[ingredient.id] = (
    #                 shop_dictary[ingredient.id][0],
    #                 shop_dictary[ingredient.id][1] + amount
    #             )
    #         else:
    #             shop_dictary[ingredient.id] = (
    #                 ingredient.__str__(),
    #                 amount)

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = Recipes.objects.all()
    #     tags = self.request.data.get('tags')
    #     if tags:
    #         queryset = queryset and Recipes.objects.filter(tags__slug__in=tags)
    #     if user.is_anonymous:
    #         return queryset
    #     try:
    #         recipe_id = self.kwargs['pk']
    #         return Recipes.objects.get(id=recipe_id)
    #     except KeyError:
    #         recipe_id = None
    #     author_id = self.request.data.get('author')
    #     if author_id:
    #         queryset = (
    #             queryset and Recipes.objects.filter(
    #                 author=get_object_or_404(User, id=author_id))
    #                 )

        # if self.request.data.get('is_favorited') == 1:
        #     queryset = queryset and user.favorite_recipes.all()
        # if self.request.data.get('is_in_shopping_cart') == 1:
        #     queryset = queryset and user.shopping_cart_recipes.all()
        # return queryset


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
    # permission_classes = (IsAuthenticated, )
    lookup_field = 'id'

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if self.request.method == 'GET':
            data = UsersSerializer(self.request.user).data
            return Response(data)

    @action(detail=True, methods=['post', 'delete'],)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if self.request.method == 'POST':
            if request.user != author:
                Follow.objects.create(user=request.user, author=author)
                data = UsersSerializer(author).data
                return Response(data)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    permission_classes = [AllowAny]


class ChangePasswordView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer


# class RecipeViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     permission_classes = (IsOwnerOrAdminOrReadOnly,)
#     pagination_class = CustomPagination
#     filter_backend = (DjangoFilterBackend, )
#     filterset_class = RecipeFilter

#     def perform_create(self, serializer):
#         return serializer.save(author=self.request.user)

#     @action(detail=True, permission_classes=[IsAuthenticated],
#             methods=['POST'])
#     def favorite(self, request, pk=None):
#         serial_type = FavoritesSerializer
#         serializer = add_favorite_or_cart(self, request, pk, serial_type)

#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     @favorite.mapping.delete
#     def delete_favorite(self, request, pk=None):
#         model = Favorites
#         delete_favorite_or_cart(self, request, pk, model)

#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(detail=True, permission_classes=[IsAuthenticated],
#             methods=['POST'])
#     def shopping_cart(self, request, pk=None):
#         serial_type = CartSerializer
#         serializer = add_favorite_or_cart(self, request, pk, serial_type)

#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     @shopping_cart.mapping.delete
#     def delete_shopping_cart(self, request, pk=None):
#         model = Cart
#         delete_favorite_or_cart(self, request, pk, model)

#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(detail=False, permission_classes=[IsAuthenticated])
#     def download_shopping_cart(self, request):
#         ingredients = IngredientsInRecipe.objects.filter(
#             recipe__carts__user=request.user).values(
#             'ingredients__name',
#             'ingredients__measurement_unit').annotate(total=Sum('amount'))
#         shopping_list = 'Список покупок:\n\n'
#         for number, ingredient in enumerate(ingredients, start=1):
#             shopping_list += (
#                 f'{ingredient["ingredients__name"]}: '
#                 f'{ingredient["total"]} '
#                 f'{ingredient["ingredients__measurement_unit"]}\n')

#         cart = 'shopping-list.txt'
#         response = HttpResponse(shopping_list, content_type='text/plain')
#         response['Content-Disposition'] = (f'attachment;'
#                                            f'filename={cart}')
#         return response


# class IngredientViewSet(viewsets.ModelViewSet):
#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
#     paginator = None
#     permission_classes = (AllowAny, )
#     filter_backends = [IngredientSearchFilter]
#     search_fields = ('^name',)
