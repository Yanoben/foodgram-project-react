from django.db import models
from users.models import UserProfile
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint


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


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name='name')
    color = models.CharField(max_length=7, verbose_name='color')
    slug = models.SlugField(unique=True, verbose_name='tag_slug')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'


class Ingredients(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='name')
    measurement_unit = models.CharField(
        max_length=10, verbose_name='measurement_unit')

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'


class Recipes(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="name",

    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='ingredients',
        related_name="recipes",
        through="RecipesIngredient"
    )
    tags = models.ManyToManyField(
        Tag,
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
        verbose_name="cooking_time",
        validators=(
            MinValueValidator(
                1,
                message="Минимальное время приготовления - одна минута"
            ),
        )
    )

    class Meta:
        verbose_name = "recipe"
        verbose_name_plural = 'recipes'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipesIngredient(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='ingredient_to_recipe')
    ingredient = models.ForeignKey(Ingredients,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_to_recipe')
    amount = models.IntegerField(default=1, related_name='amount')

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
        related_name='favorites',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='recipe'
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='recipe'
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='shopping_cart')
        ]
        verbose_name = 'shopping_cart'
        verbose_name_plural = 'shopping_carts'


class Follow(models.Model):
    user = models.ForeignKey(UserProfile,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='user')
    author = models.ForeignKey(UserProfile,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='author')

    class Meta:
        fields = UniqueConstraint(
            fields=['user', 'author'], name='follow')
        verbose_name = 'follow'
        verbose_name_plural = 'follows'
