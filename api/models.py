from django.db import models


class User(models.Model):
    _id = models.CharField(max_length=50)
    role = models.CharField(max_length=10)
    name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=150, null=True)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=25, null=True)
    institution = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    activated = models.BooleanField()


class Catalog(models.Model):
    _id = models.CharField(max_length=50)
    name = models.CharField(max_length=150, null=True)
    type = models.CharField(max_length=50)
    values = models.JSONField(null=True)


class Project(models.Model):
    _id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    season = models.CharField(max_length=50)
    admin_users = models.JSONField(null=True)
    activated = models.BooleanField()
