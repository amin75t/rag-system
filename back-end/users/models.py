from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.phone
