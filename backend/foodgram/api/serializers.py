from rest_framework import serializers
# from drf_extra_fields.fields import Base64ImageField
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

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


# class IngredientRecipeSerializer(serializers.ModelSerializer):
#     amount = serializers.SerializerMethodField('get_amount')

#     class Meta:
#         model = Ingredients
#         fields = ('id', 'name', 'measurement_unit', 'amount')

#     def get_amount(self, obj):
#         return RecipesIngredient.objects.get(ingredients=obj).amount


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
        model = RecipesIngredient
        fields = ('id', 'amount')


# class CreateRecipeSerializer(serializers.ModelSerializer):
#     image = Base64ImageField()
#     tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all())
#     ingredients = RecipeIngredientsSerializer()

#     class Meta:
#         model = Recipes
#         fields = ('tags', 'ingredients',
#                   'name', 'image', 'text', 'cooking_time')
#         read_only_fields = ("author",)

#     def validate(self, data):
#         ingredients = self.data.get("ingredients")
#         if not ingredients:
#             raise serializers.ValidationError(
#                 "Рецепту обязательно нужны ингридиенты!"
#             )
#         ingredient_list = []
#         for ingredient_item in ingredients:
#             ingredient = get_object_or_404(
#                 Ingredients,
#                 id=ingredient_item["id"],
#             )
#             if ingredient in ingredient_list:
#                 raise serializers.ValidationError(
#                     "Пожалуйста, не дублируйте ингридиенты!"
#                 )
#             ingredient_list.append(ingredient)
#             if int(ingredient_item["amount"]) < 0:
#                 raise serializers.ValidationError(
#                     "Количество ингредиента должно быть больше 0!"
#                 )
#         data["ingredients"] = ingredients
#         return data

    # def update(self, instance, validated_data):
    #     user = self.context['request'].user
    #     if user != instance.author:
    #         serializers.ValidationError(
    #             'Нельзя редактировать чужой рецепт'
    #         )
    #     instance.name = validated_data['name']
    #     instance.text = validated_data['text']
    #     instance.cooking_time = validated_data['cooking_time']
    #     instance.image = validated_data['image']
    #     instance.save()
    #     tags = self.context['request'].data['tags']
    #     RecipesTag.objects.filter(recipe=instance).delete()
    #     for tag in tags:
    #         RecipesTag.objects.create(
    #             recipe=instance,
    #             tag=Tags.objects.get(id=tag)
    #         )
    #     ingredients = self.context['request'].data['ingredients']
    #     RecipesIngredient.objects.filter(recipe=instance).delete()
    #     for ingredient in ingredients:
    #         RecipesIngredient.objects.create(
    #             recipe=instance,
    #             ingredient=Ingredients.objects.get(id=ingredient['id']),
    #             amount=ingredient['amount']
    #         )
        # return instance


class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UsersSerializer(required=False, read_only=True)
    ingredients = RecipesIngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True)
    ingredients = RecipesIngredientSerializer(
        many=True, queryset=Ingredients.objects.all())
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

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
        return RecipesSerializer(
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
    recipes = RecipesSerializer(read_only=True, many=True,
                                source='author.recipes')
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'is_subscribed',
                  'recipes_count')
