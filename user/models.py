from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, default=None)
    email = models.EmailField(unique=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.group is None:
            self.group = Group.objects.get(name='normal')
        super().save(*args, **kwargs)
