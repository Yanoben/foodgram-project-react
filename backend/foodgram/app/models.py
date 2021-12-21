from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields import TextField

User = get_user_model()


class Tags(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)


class Ingredients(models.Model):
    name = models.CharField(max_length=100)
    amount = models.IntegerField(help_text='Количество')
    units = TextField(help_text='Единицы измерения')


class Recipes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    title = models.CharField(max_length=50)
    image = models.ImageField()
    ingredients = models.ForeignKey(Ingredients, related_name='recipes')
    tag = models.Model(Tags)
    ready_time = models.TimeField()
