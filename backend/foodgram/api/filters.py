from django_filters.rest_framework import FilterSet, filters

from app.models import Ingredient, Recipe, Tag


class RecipeTagFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = [
            'author', 'tags'
        ]

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        if not self.request.user.is_authenticated:
            return queryset
        favorites = self.request.user.favorites.all()
        return queryset.filter(
            pk__in=(favorites.values_list('id', flat=True,))
        )

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


class IngredientsFilter(FilterSet):
    ingredients = filters.ModelMultipleChoiceFilter(
        field_name='ingredients__name',
        lookup_expr='istartswith',
        to_field_name='name',
        queryset=Ingredient.objects.all(),
        method='get_ingredient'
    )

    def get_ingredient(self, queryset, name):
        queryset = queryset.filter(name=name)
        return queryset

    class Meta:
        model = Ingredient
        fields = [
            'name',
        ]
