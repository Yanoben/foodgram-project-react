from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import RecipesFilter
from .mixins import ModelMixinSet
from .permissions import (AdminAuthorPermission, AdminOnly,
                          IsAdminUserOrReadOnly)
from app.models import Tags, Ingredients, Recipes
from .serializers import (SignupSerializer, GetTokenSerializer,
                          RecipesSerializer, TagsSerializer,
                          IngredSerializer, UsersSerializer,
                          ChangePasswordSerializer)
from django.conf import settings
from users.models import UserProfile
from rest_framework import generics


User = settings.AUTH_USER_MODEL


class TagsViewSet(ModelMixinSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = [SearchFilter, ]
    search_fields = ['name', ]


class IngredientsViewSet(ModelMixinSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = [SearchFilter, ]
    search_fields = ['name', ]


class RecipesViewSet(ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination
    filter_class = RecipesFilter
    # search_fields = ['title', ]


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
            user = UserProfile.objects.get(username=data['username'])
        except UserProfile.DoesNotExist:
            return Response({'username': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if data.get('password') == user.password:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response({'Password': 'Wrong password!'},
                        status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UsersSerializer
    filter_backends = [SearchFilter, ]
    search_fields = ('username', )
    pagination_class = PageNumberPagination

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


class ChangePasswordView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
