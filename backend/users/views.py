from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from api.serializers import FollowSerializer

from .models import Follow, User
from .serializers import CustomUserSerializer


class CustomUserViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = User.objects.get(pk=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(follower=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            return self.add_subscribe(Follow, request, id)
        elif request.method == 'DELETE':
            return self.del_subscribe(Follow, request, id)

    def add_subscribe(self, model, request, id):
        follower = request.user
        user = get_object_or_404(User, id=id)
        if user == follower:
            raise ValidationError(
                {'errors': 'Вы не можете подписаться на самого себя.'}
            )
        elif model.objects.filter(user=user, follower=follower).exists():
            raise ValidationError(
                {'errors': 'Вы уже подписаны на этого пользователя.'}
            )
        follow = model.objects.create(user=user, follower=follower)
        serializer = FollowSerializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_subscribe(self, model, request, id):
        follower = request.user
        user = get_object_or_404(User, id=id)
        if user == follower:
            raise ValidationError(
                {'errors': 'Вы не можете отписаться от самого себя.'}
            )
        elif model.objects.filter(user=user, follower=follower).exists():
            model.objects.filter(user=user, follower=follower).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError(
            {'errors': 'Вы не подписаны на этого пользователя.'}
        )
