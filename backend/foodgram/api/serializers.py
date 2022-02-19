from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.conf import settings
from app.models import (Follow, Recipes, Tags, Ingredients, ShoppingCart,
                        RecipesIngredient, FavoriteRecipes)
from users.models import UserProfile
from six import string_types
import base64
import uuid
from django.core.files.base import ContentFile
import imghdr


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


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tags


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=RecipesIngredient.objects.all(),
                fields=['ingredients', 'recipes']
            )
        ]


class IngredientToCreateRecipeSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(), many=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = ("id", "amount")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredients
        fields = ('id', 'amount')
        read_only_fields = ('id',)

    def get_amount(self, obj):
        return obj.amount.get().value


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientToCreateRecipeSerializer(many=True)
    # tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'ingredients', 'tags',
            'image', 'name',
            'text', 'cooking_time'
            )
        read_only_fields = ('id', 'author')

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmountSerializer.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        tags_data = self.initial_data.get('tags')
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
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'ingredients error'}
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredients, id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Double ingredients'
                )
            if not ingredient_item['amount'].isdigit():
                raise serializers.ValidationError(
                    'only number'
                )
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
        user = self.context['request'].user
        return (
                user.is_authenticated
                and obj.favorite_recipes.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
                user.is_authenticated
                and obj.in_shopping_cart.filter(user=user).exists()
        )


class RetrieveRecipesSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    # tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientToCreateRecipeSerializer(many=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False)

    class Meta:
        model = Recipes
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
        model = Recipes
        fields = ('id', 'name', 'cooking_time',)
        read_only_fields = ('id',)


# class UserSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             'password',
#         ]
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def get_is_subscribed(self, obj):
#         user = self.context['request'].user
#         if not user.is_authenticated:
#             return False
#         return Subscription.objects.filter(
#             subscriber=user,
#             subscription=obj,
#         ).exists()

#     def create(self, validated_data):
#         validated_data['password'] = (
#             make_password(validated_data.pop('password'))
#         )
#         return super().create(validated_data)
