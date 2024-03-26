from django.db import models


class User(models.Model):
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=25)
    institution = models.CharField(max_length=255)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    activated = models.BooleanField()
    role = models.CharField(max_length=10)
