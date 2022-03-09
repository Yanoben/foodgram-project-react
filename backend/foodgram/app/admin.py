from django.contrib import admin
from users.models import UserProfile

from .models import Ingredients, Recipes, Tags

admin.site.register(Recipes)
admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(UserProfile)


class RecipesAdmin(admin.ModelAdmin):

    list_display = ('name', 'ingredients', 'tags', 'text',
                    'image', 'cooking_time')
    list_select_related = (
        'name',
    )
