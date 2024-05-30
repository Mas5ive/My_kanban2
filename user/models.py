from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    last_login = None

    objects = BaseUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
