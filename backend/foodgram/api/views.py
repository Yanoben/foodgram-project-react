from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from .mixins import ModelMixinSet
from .permissions import (AdminModeratorAuthorPermission, AdminOnly,
                          IsAdminUserOrReadOnly)
from app.models import Tags, Ingredients, Recipes
# from .serializers import (CategorySerializer, CommentsSerializer,
#                           GenreSerializer, GetTokenSerializer,
#                           NotAdminSerializer, ReviewSerializer,
#                           SignupSerializer, TitleReadSerializer,
#                           TitleWriteSerializer, UsersSerializer)
from .serializers import (SignupSerializer, GetTokenSerializer,
                          RecipesSerializer, TagsSerializer)
from django.conf import settings


User = settings.AUTH_USER_MODEL


class TagsViewSet(ModelMixinSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminUserOrReadOnly,
                          AdminModeratorAuthorPermission)
    lookup_field = 'slug'
    filter_backends = [SearchFilter, ]
    search_fields = ['name', ]


class IngredientsViewSet(ModelMixinSet):
    queryset = Ingredients.objects.all()
    # serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = [SearchFilter, ]
    search_fields = ['name', ]


class RecipesViewSet(ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = RecipesSerializer


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
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response({'username': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response({'confirmation_code': 'Wrong confirmation code!'},
                        status=status.HTTP_400_BAD_REQUEST)


# class UsersViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UsersSerializer
#     permission_classes = (IsAuthenticated, AdminOnly,)
#     lookup_field = 'username'
#     filter_backends = [SearchFilter, ]
#     search_fields = ('username', )
#     pagination_class = PageNumberPagination

#     @action(methods=['GET', 'PATCH'], detail=False,
#             permission_classes=[IsAuthenticated, ],
#             url_path='me')
#     def current_user(self, request):
#         if request.method == 'PATCH':
#             if request.user.is_admin:
#                 serializer = UsersSerializer(request.user, data=request.data,
#                                              partial=True)
#             else:
#                 serializer = NotAdminSerializer(request.user,
#                                                 data=request.data,
#                                                 partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         serializer = UsersSerializer(request.user)
#         return Response(serializer.data)
