from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import ROLES
# from .validators import (validate_username_me,
#                          validate_year)


USER = 'user'
ADMIN = 'admin'
CHOICES = (
    (USER, 'user'),
    (ADMIN, 'admin'),
)


class UserProfile(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_subscribed = models.BooleanField(default=False)
    role = models.CharField(max_length=16, choices=CHOICES,
                            default=USER, blank=True)

    @property
    def is_user(self):
        return self.role == ROLES['USER_ROLE']

    @property
    def is_admin(self):
        return self.role == ROLES['ADMIN_ROLE']

    class Meta:
        ordering = ['-username', ]

    def __str__(self):
        return self.username
