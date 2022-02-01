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
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


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
        fields = ('id', 'name', 'color', 'slug')
        model = Tags


class IngredientSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source='ingredients.id')
    # name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'amount')
        read_only_fields = ('id',)

    def get_amount(self, obj):
        return obj.amount.get().value


class RecipesIngredientSerializer(serializers.PrimaryKeyRelatedField,
                                  serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    # def get_amount(self, obj):
        # return RecipesIngredient.objects.get(ingredients=obj).amount


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = Ingredients
        fields = ('id', 'amount')

    def get_amount(self, obj):
        return RecipesIngredient.objects.get(ingredients=obj).amount


# class RecipesSerializer(serializers.ModelSerializer):
#     image = Base64ImageField()
#     author = UsersSerializer(required=False, read_only=True)
#     ingredients = RecipesIngredientSerializer(many=True, read_only=True)
#     tags = TagSerializer(read_only=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()

#     class Meta:
#         model = Recipes
#         fields = ('id', 'tags', 'author', 'ingredients',
#                   'is_favorited', 'is_in_shopping_cart',
#                   'name', 'image', 'text', 'cooking_time')
#         read_only_fields = ('id', 'is_favorited', 'is_in_shopping_cart')

#     def get_is_favorited(self, obj):
#         user = self.context['request'].user
#         if user.is_anonymous:
#             return False
#         return FavoriteRecipes.objects.filter(user=user, recipe=obj).exists()

#     def get_is_in_shopping_cart(self, obj):
#         user = self.context['request'].user
#         if user.is_anonymous:
#             return False
#         return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RetrieveRecipesSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    ingredients = IngredientSerializer(read_only=True)
    tags = TagSerializer(read_only=True)

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time'
                  )
        model = Recipes


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipes
        fields = ('id', 'author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipesIngredient.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount'])

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipesIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RetrieveRecipesSerializer(
            instance, context=context).data


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
