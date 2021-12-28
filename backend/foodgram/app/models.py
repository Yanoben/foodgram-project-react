from django.conf import settings
from django.db import models
from django.db.models.fields import TextField
from colorfield.fields import ColorField

User = settings.AUTH_USER_MODEL


class Tags(models.Model):
    name = models.CharField(max_length=20)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True, verbose_name='tags_slug')


class Ingredients(models.Model):
    name = models.CharField(max_length=100)
    amount = models.IntegerField(help_text='Количество')
    units = TextField(help_text='Единицы измерения')


class Recipes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    title = models.CharField(max_length=50)
    image = models.ImageField()
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE,
                                    related_name='recipes')
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    ready_time = models.TimeField()
