from django.contrib import admin

from users.models import UserProfile
from .models import Ingredient, Recipe, Tag

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(UserProfile)


class RecipesAdmin(admin.ModelAdmin):

    list_display = ('name', 'ingredients', 'tags', 'text',
                    'image', 'cooking_time')
    list_select_related = (
        'name',
    )
