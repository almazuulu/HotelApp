from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Project user model, fixed before the first migration as required by Django."""

    email = models.EmailField("email address", unique=True)
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    phone = models.CharField(max_length=32)

    REQUIRED_FIELDS = ["email", "first_name", "last_name", "phone"]
