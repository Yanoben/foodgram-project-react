from asyncore import read
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.conf import settings
from app.models import (Follow, Recipes, Tags, Ingredients, ShoppingCart,
                        RecipesIngredient, Favorite)
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


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipesIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField(source='recipesingredient.amount')

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientToCreateRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(), many=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = ("id", "amount")


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientToCreateRecipeSerializer(many=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
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
            RecipesIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(image=image, **validated_data)
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
    # def favorite_or_shopping_cart_same_logic(self, request, cls, err_msg):
    #     user = request.user
    #     recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
    #     obj = cls.objects.filter(user=user, recipe=recipe)
    #     if request.method == 'POST':
    #         if obj.exists():
    #             data = {'errors': f'Рецепт уже в {err_msg}!'}
    #             return response.Response(
    #                 data=data, status=status.HTTP_400_BAD_REQUEST
    #             )
    #         cls.objects.create(user=user, recipe=recipe)
    #         serializer = self.get_serializer(recipe)
    #         return response.Response(
    #             data=serializer.data, status=status.HTTP_201_CREATED
    #         )
    #     if obj.exists():
    #         obj.delete()
    #         return response.Response(status=status.HTTP_204_NO_CONTENT)
    #     data = {'errors': f'Рецепт отсутствует в {err_msg}!'}
    #     return response.Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    # @decorators.action(detail=True, methods=['POST', 'DELETE'])
    # def favorite(self, request, pk=None):
    #     cls = Favorite
    #     err_msg = 'избранном'
    #     return self.favorite_or_shopping_cart_same_logic(request, cls, err_msg)

    # @decorators.action(detail=True, methods=['POST', 'DELETE'])
    # def shopping_cart(self, request, pk=None):
    #     cls = ShoppingCart
    #     err_msg = 'списке покупок'
    #     return self.favorite_or_shopping_cart_same_logic(request, cls, err_msg)


class RetrieveRecipesSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(many=True, read_only=True)
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
