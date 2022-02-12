from django.db import models
from colorfield.fields import ColorField
from users.models import UserProfile
from django.core.validators import MinValueValidator


# class Recipe(models.Model):
#     name = models.CharField(
#         max_length=200,
#         verbose_name="Название рецепта",

#     )
#     ingredients = models.ManyToManyField(
#         Ingredient,
#         verbose_name="Ингредиенты",
#         related_name="recipes",
#         through="IngredientInRecipe"
#     )
#     tags = models.ManyToManyField(
#         Tag,
#         verbose_name="Тэги",
#         related_name="recipes"
#     )
#     author = models.ForeignKey(
#         User,
#         verbose_name="Автор",
#         related_name="recipes",
#         on_delete=models.CASCADE
#     )
#     text = models.TextField(
#         verbose_name="Текст рецепта"
#     )
#     image = models.ImageField(
#         verbose_name="Картинка",
#         upload_to='media/recipes/images/'
#     )
#     cooking_time = models.PositiveSmallIntegerField(
#         verbose_name="Время приготовления в минутах",
#         validators=(
#             MinValueValidator(
#                 1,
#                 message="Минимальное время приготовления - одна минута"
#             ),
#         )
#     )


class Tags(models.Model):
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=7)
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
    # author = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
    #                            related_name='recipes')
    # ingredients = models.ManyToManyField(Ingredients,
    #                                      through='RecipesIngredient',
    #                                      related_name="recipes")
    # tags = models.ForeignKey(Tags, on_delete=models.CASCADE,
    #                          related_name='recipes')
    # image = models.ImageField()
    # name = models.CharField(default='name', max_length=200)
    # text = models.TextField(default='Text')
    # cooking_time = models.IntegerField(default='1')

    # def __str__(self):
    #     return self.name
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",

    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name="Ингредиенты",
        related_name="recipes",
        through="RecipesIngredient"
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name="Тэги",
        related_name="recipes"
    )
    author = models.ForeignKey(
        UserProfile,
        verbose_name="Автор",
        related_name="recipes",
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name="Текст рецепта"
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to='media/recipes/images/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        validators=(
            MinValueValidator(
                1,
                message="Минимальное время приготовления - одна минута"
            ),
        )
    )

    class Meta:
        ordering = ['-id']


class RecipesIngredient(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='ingredient_to_recipe')
    ingredient = models.ForeignKey(Ingredients,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_to_recipe')
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
    user = models.ForeignKey(
        UserProfile,
        verbose_name="Автор",
        related_name="favorite_user",
        on_delete=models.CASCADE
    )
    recipes = models.ForeignKey(Recipes, default='recipes',
                                on_delete=models.CASCADE,
                                related_name='favorite_recipe')

    class Meta:
        ordering = ['-user']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipes'),
                name='user_recipe_favorite'
            )
        ]


class ShoppingCart(models.Model):
    pass
    # user = models.ForeignKey(
    #     UserProfile,
    #     related_name="shopping_cart",
    #     on_delete=models.CASCADE
    # )
    # recipe = models.ForeignKey(
    #     Recipes,
    #     related_name="shopping_cart",
    #     on_delete=models.CASCADE
    # )

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=["user", "recipe"],
    #                                 name="unique_shopping_list")
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
