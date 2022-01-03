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
    measurement_unit = TextField(default='Kg')


class Recipes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE,)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    image = models.ImageField()
    name = models.CharField(default='Food', max_length=200)
    text = models.TextField(default='Text')
    cooking_time = models.IntegerField(default='1')
    pub_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        ordering = ['-pub_date', ]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ('user', 'author',)
