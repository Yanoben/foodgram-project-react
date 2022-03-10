from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .fields import Base64ImageField
from app.models import (Favorite, Follow, Ingredient, Recipe,
                        RecipeIngredient, ShoppingCart, Tag)
from users.models import UserProfile

User = settings.AUTH_USER_MODEL


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password"
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = UserProfile.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientAmountSerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField(source='recipeingredient.amount')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientToCreateRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), many=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientToCreateRecipeSerializer(many=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags',
            'image', 'name',
            'text', 'cooking_time'
            )
        read_only_fields = ('id', 'author')

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = validated_data.pop('tags')
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'ingredients error'}
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Double ingredients'
                )
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество не может быть меньше нуля'
                })
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Amount need more then 0'
                    }
                )
        data['ingredients'] = ingredients
        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class RetrieveRecipesSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(many=True, read_only=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart',
            'name', 'image', 'text',
            'cooking_time'
        )


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'password')


class GetTokenSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = UserProfile
        fields = ('password', 'email')


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserProfile
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = RetrieveRecipesSerializer(read_only=True, many=True,
                                        source='author.recipes')
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'is_subscribed',
                  'recipes_count')


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time',)
        read_only_fields = ('id',)
