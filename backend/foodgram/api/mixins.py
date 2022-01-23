from rest_framework import mixins, viewsets
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


class ModelMixinSet(CreateModelMixin, ListModelMixin, DestroyModelMixin,
                    GenericViewSet):
    pass


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class AddingAndDeletingListMixin:
    serializer_class = None
    model_class = None

    def get(self, request, recipe_id):
        user = request.user.id
        data = {"user": user, "recipe": recipe_id}
        serializer = self.serializer_class(
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        obj = get_object_or_404(
            self.model_class, user=user, recipe__id=recipe_id
        )
        obj.delete()
        model_title = self.model_class._meta.verbose_name.title()
        return Response(
            f"Успешно удалено: {model_title}!", status.HTTP_204_NO_CONTENT
        )


class FavoriteViewSet(AddingAndDeletingListMixin, APIView):
    serializer_class = FavoriteSerializer
    model_class = Favorite


class PurchaseListView(AddingAndDeletingListMixin, APIView):
    serializer_class = PurchaseListSerializer
    model_class = PurchaseList


class SubscribeView(AddingAndDeletingListMixin, APIView):
    serializer_class = SubscribeSerializer
    model_class = Subscribe
