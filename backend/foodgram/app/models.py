from django.conf import settings
from django.db import models
from django.db.models.fields import TextField
from colorfield.fields import ColorField
from users.models import UserProfile


class Tags(models.Model):
    name = models.CharField(max_length=20)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True, verbose_name='tags_slug')


class Ingredients(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = TextField(default='Kg')


class Recipes(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                               related_name='recipes')
    ingredients = models.ForeignKey(Ingredients, on_delete=models.DO_NOTHING)
    tags = models.ForeignKey(Tags, on_delete=models.DO_NOTHING)
    image = models.ImageField()
    name = models.CharField(default='Food', max_length=200)
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    text = models.TextField(default='Text')
    cooking_time = models.IntegerField(default='1')
    pub_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        ordering = ['-pub_date', ]


class Follow(models.Model):
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(UserProfile,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ('user', 'author',)
