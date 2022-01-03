from django.contrib import admin
from .models import Recipes, Tags, Ingredients
from users.models import UserProfile

admin.site.register(Recipes)
admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(UserProfile)
