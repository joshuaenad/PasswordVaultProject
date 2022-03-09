from cryptography.fernet import Fernet
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Password(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner", null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    url = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    logo = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]