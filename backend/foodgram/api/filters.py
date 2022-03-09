from app.models import Ingredients, Recipes, Tags
from django_filters.rest_framework import FilterSet, filters


class RecipeTagFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )
    # is_favorited = filters.BooleanFilter(method='get_is_favorited')
    # is_in_shopping_cart = filters.BooleanFilter(
    #     method='get_is_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = [
            'author', 'tags'
        ]

    # def get_is_favorited(self, queryset, name, value):
    #     if not value:
    #         return queryset
    #     if not self.request.user.is_authenticated:
    #         return queryset
    #     favorites = self.request.user.favorites.all()
    #     return queryset.filter(
    #         pk__in=(favorites.values_list('id', flat=True,))
    #     )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        if not self.request.user.is_authenticated:
            return queryset
        if not self.request.user.shopping_cart.recipes.exists():
            return queryset
        recipes = (
            self.request.user.shopping_cart.recipes.all()
        )
        return queryset.filter(
            pk__in=(recipes.values_list('id', flat=True))
        )

    # def filter_is_favorited(self, queryset, name, value):
    #     user = self.request.user
    #     if value:
    #         return Recipes.objects.filter(favorite_recipes__user=user)
    #     return queryset

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


class IngredientsFilter(FilterSet):
    ingredients = filters.ModelMultipleChoiceFilter(
        field_name='ingredients__name',
        lookup_expr='istartswith',
        to_field_name='name',
        queryset=Ingredients.objects.all(),
        method='get_ingredient'
    )

    def get_ingredient(self, queryset, name):
        queryset = queryset.filter(name=name)
        return queryset

    class Meta:
        model = Ingredients
        fields = [
            'name',
        ]
