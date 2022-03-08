from django.db import models
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
        return f'{self.name} {self.measurement_unit}'

    class Meta:
        verbose_name = 'ingredients'


class Recipes(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",

    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='ingredients',
        related_name="recipes",
        through="RecipesIngredient"
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name="tags",
        related_name="recipes"
    )
    author = models.ForeignKey(
        UserProfile,
        verbose_name="author",
        related_name="recipes",
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name="text"
    )
    image = models.ImageField(
        verbose_name="image",
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
        verbose_name = "recipes"
        ordering = ['-id']

    def __str__(self):
        return self.name


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
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='shopping_cart')
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Follow(models.Model):
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(UserProfile,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ('user', 'author',)
