from django_filters.rest_framework import filters, FilterSet

from app.models import Recipes


class RecipeTagFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipes.objects.filter(favorite_recipes__user=user)
        return queryset

    # class Meta:
    #     model = Recipe
    #     fields = ['tags__slug', 'is_favorited']
    # tags = filters.AllValuesMultipleFilter(
    #     field_name='tags__slug')
    # author = filters.NumberFilter(
    #     field_name='author__id')
    # # is_favorited = django_filters.BooleanFilter(field_name='is_favorited')
    # # is_in_shopping_cart = django_filters.BooleanFilter(
    # #     field_name='is_in_shopping_cart')

    # class Meta:
    #     model = Recipes
    #     fields = ('tags', 'author')
