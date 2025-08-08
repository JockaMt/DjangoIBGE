from django.db import models

# Create your models here.
class User(models.Model):
    name = models.TextField(max_length=25, unique=True)
    email = models.TextField(max_length=50, unique=True)
    password_hash = models.TextField(max_length=255)