import django_filters

from app.models import Recipes


class RecipeTagFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='tags__slug')
    # is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    # is_in_shopping_cart = django_filters.NumberFilter(
    #     method='filter_is_in_shopping_cart')
    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart')

    # def filter_is_favorite(self, queryset, name, value):
    #     if value is True:
    #         return queryset.filter(favorite_recipe__user=self.request.user)
    #     else:
    #         return queryset.filter(favorite_recipe__user__isnull=True)

    class Meta:
        model = Recipes
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart', 'author')
