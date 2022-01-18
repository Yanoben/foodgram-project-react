# from django.conf import settings
from django.db import models
from django.db.models.fields import TextField
from colorfield.fields import ColorField
from users.models import UserProfile


class Tags(models.Model):
    name = models.CharField(max_length=20)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True, verbose_name='tags_slug')

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = TextField(default='Kg')

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                               related_name='recipes')
    ingredients = models.ManyToManyField(Ingredients,
                                         through='RecipesIngredient')
    tags = models.ManyToManyField(Tags, through='RecipesTag')
    image = models.ImageField()
    name = models.CharField(default='Food', max_length=200)
    text = models.TextField(default='Text')
    cooking_time = models.IntegerField(default='1')
    pub_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.name


class RecipesTag(models.Model):
    recipes = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tags, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipes} {self.tags}'


class RecipesIngredient(models.Model):
    recipes = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipes} {self.ingredients}'


class FavoriteRecipes(models.Model):
    pass


class ShoppingCart(models.Model):
    pass


class Follow(models.Model):
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(UserProfile,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ('user', 'author',)
