from rest_framework import serializers

from django.conf import settings
from app.models import Recipes, Tags, Ingredients
from users.models import UserProfile


User = settings.AUTH_USER_MODEL


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ['id']
        model = Tags
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class IngredSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredients


class RecipesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Recipes


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    confirmation_code = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'first_name',
                  'last_name', 'role')


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'role')
        read_only_fields = ('role',)
