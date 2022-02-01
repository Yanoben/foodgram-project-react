from django.db import models
from colorfield.fields import ColorField
from users.models import UserProfile


class Tags(models.Model):
    name = models.CharField(max_length=20)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True, verbose_name='tags_slug')

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='name', blank=False)
    measurement_unit = models.CharField(
        max_length=10, verbose_name='measurement_unit', blank=False)

    def __str__(self):
        return f'{self.name}'


class Recipes(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                               related_name='recipes')
    ingredients = models.ManyToManyField(Ingredients,
                                         through='RecipesIngredient')
    tags = models.ForeignKey(Tags, on_delete=models.CASCADE,
                             related_name='recipes')
    image = models.ImageField()
    name = models.CharField(default='name', max_length=200)
    text = models.TextField(default='Text')
    cooking_time = models.IntegerField(default='1')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipesIngredient(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipes} {self.ingredients}'


class FavoriteRecipes(models.Model):
    pass
    # user = models.ForeignKey(UserProfile,
    #                          on_delete=models.CASCADE,
    #                          related_name='favorite_user')
    # recipes = models.ForeignKey(Recipes, default='recipes',
    #                             on_delete=models.CASCADE,
    #                             related_name='favorite_recipe')

    # class Meta:
    #     ordering = ['-user']
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=('user', 'recipes'),
    #             name='user_recipe_favorite'
    #         )
    #     ]


class ShoppingCart(models.Model):
    pass
    # user = models.ForeignKey(UserProfile,
    #                          on_delete=models.CASCADE,
    #                          related_name='shopping')
    # recipe = models.ForeignKey(Recipes,
    #                            on_delete=models.CASCADE,
    #                            related_name='shopping')

    # class Meta:
    #     ordering = ['-user']
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=('user', 'recipe'),
    #             name='user_recipe_shopping'
    #         )
    #     ]


class Follow(models.Model):
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(UserProfile,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ('user', 'author',)
