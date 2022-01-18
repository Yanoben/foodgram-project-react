from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.conf import settings
from app.models import (Recipes, Tags, Ingredients, ShoppingCart, RecipesTag,
                        RecipesIngredient, FavoriteRecipes)
from users.models import UserProfile


User = settings.AUTH_USER_MODEL


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tags
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField('get_amount')

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        return RecipesIngredient.objects.get(ingredients=obj).amount


# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
    # queryset=Ingredients.objects.all())
#     name = serializers.ReadOnlyField(source='ingredient.name')
#     measurement_unit = serializers.ReadOnlyField(
#         source='ingredient.measurement_unit')
#     amount = serializers.IntegerField()

#     class Meta:
#         model = RecipesIngredient
#         fields = ('id', 'name', 'measurement_unit', 'amount')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True)
    author = UsersSerializer(required=False, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='ingredients_from_recipe',
        read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
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

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user != instance.author:
            serializers.ValidationError(
                'Нельзя редактировать чужой рецепт'
            )
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        instance.image = validated_data['image']
        instance.save()
        tags = self.context['request'].data['tags']
        RecipesTag.objects.filter(recipe=instance).delete()
        for tag in tags:
            RecipesTag.objects.create(
                recipe=instance,
                tag=Tags.objects.get(id=tag)
            )
        ingredients = self.context['request'].data['ingredients']
        RecipesIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            RecipesIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        return instance

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_anonymous:
            serializers.ValidationError(
                'Авторизуйтесь, чтобы добавить рецепт')
        recipe = Recipes.objects.create(
            author=user,
            name=validated_data['name'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time'],
            image=validated_data['image']
        )
        tags = self.context['request'].data['tags']
        for tag in tags:
            RecipesTag.objects.create(
                recipe=recipe,
                tag=Tags.objects.get(id=tag)
            )
        ingredients = self.context['request'].data['ingredients']
        for ingredient in ingredients:
            RecipesIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        return recipe


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


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
