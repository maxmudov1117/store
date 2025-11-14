from django.db import models
from django.contrib.auth.models import AbstractUser
from main.models import *


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField()
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username
