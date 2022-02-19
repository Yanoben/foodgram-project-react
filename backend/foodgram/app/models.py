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

    class Meta:
        verbose_name = 'ingredients'


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


class FavoriteRecipes(models.Model):
    pass
    # user = models.ForeignKey(
    #     UserProfile,
    #     verbose_name="Автор",
    #     related_name="favorite_user",
    #     on_delete=models.CASCADE
    # )
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

# class User(AbstractUser):
#     class UserType(models.TextChoices):
#         ADMIN = 'admin', _('Admin')
#         USER = 'user', _('User')

#     email = models.EmailField(
#         verbose_name='Почтовый адрес',
#         max_length=254,
#         unique=True,
#     )
#     password = models.CharField(
#         verbose_name='Пароль',
#         max_length=150,
#     )
#     username = models.CharField(
#         verbose_name='Логин',
#         max_length=150,
#         unique=True,
#     )
#     first_name = models.CharField(
#         verbose_name='Имя',
#         max_length=150,
#     )
#     last_name = models.CharField(
#         verbose_name='Фамилия',
#         max_length=150,
#     )
#     role = models.CharField(
#         verbose_name='Роль',
#         max_length=20,
#         choices=UserType.choices,
#         default=UserType.USER,
#     )
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

#     class Meta:
#         verbose_name = _('Пользователь')
#         verbose_name_plural = _('Пользователи')
#         ordering = ['id']

#     def __str__(self):
#         return self.get_full_name()

#     @property
#     def is_admin(self):
#         return self.role == self.UserType.ADMIN or self.is_staff


# class Subscription(models.Model):
#     subscriber = models.ForeignKey(
#         User,
#         related_name='subscriptions',
#         on_delete=models.CASCADE,
#     )
#     subscription = models.ForeignKey(
#         User,
#         related_name='subscribers',
#         on_delete=models.CASCADE,
#     )

#     class Meta:
#         verbose_name = 'Список подписок'
#         verbose_name_plural = 'Списки подписок'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['subscriber', 'subscription'],
#                 name='Уникальная запись подписчик - автор',
#             )
#         ]

#     def __str__(self):
#         return f'{self.subscriber} подписан на {self.subscription}'
