from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag,)
from users.models import Follow
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
                fields=['ingredient', 'recipe'],
            )
        ]


class LowerRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadOnlyRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='ingredient_recipe',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        user = request.user.pk
        recipe = obj.pk
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        user = request.user.pk
        recipe = obj.pk
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class RecipeSerializer(ReadOnlyRecipeSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError('Укажите хотя бы один тег.')
        if len(tags) != len(set(tags)):
            raise ValidationError('Теги не должны повторяться.')
        for tag in tags:
            get_object_or_404(Tag, pk=tag)
        data['tags'] = tags

        ingredients_list = []
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Укажите хотя бы один ингредиент.')
        for ingredient in ingredients:
            get_object_or_404(Ingredient, pk=ingredient['id'])
            try:
                int(ingredient['amount'])
            except ValueError:
                raise ValidationError(
                    'Количество ингредиента должно быть записано только в '
                    'виде числа.'
                )
            if int(ingredient['amount']) < 0:
                raise ValidationError('Минимальное количество игредиента - 0.')
            if ingredient in ingredients_list:
                raise ValidationError('Ингредиенты не должны повторяться.')
            ingredients_list.append(ingredient)
        data['ingredients'] = ingredients_list

        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise ValidationError('Минимальное время приготовления - 1 мин.')
        return data

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, request, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.get(pk=request.id)
        recipe.ingredients.clear()
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='user.email')
    id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = Follow

    def get_is_subscribed(self, obj):
        user = obj.user
        follower = self.context.get('request').user
        return Follow.objects.filter(user=user, follower=follower).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.user)
        serializer = LowerRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.user).count()
