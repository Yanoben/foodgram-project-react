from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin

from users.models import Follow

from .models import User

TokenAdmin.raw_id_fields = ['user']


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
    )
    search_fields = ('username', 'first_name', 'last_name')
    empty_value_display = '-пусто-'
    list_filter = ('email', 'first_name')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'follower')
    list_filter = ('user', 'follower')
    autocomplete_fields = ('user', 'follower',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
