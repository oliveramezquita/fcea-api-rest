from django.db import models


class User(models.Model):
    _id = models.CharField(max_length=50)
    role = models.CharField(max_length=10)
    email = models.CharField(max_length=255)
    activated = models.BooleanField()
    name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=150, null=True)
    phone = models.CharField(max_length=25, null=True)
    institution = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)


class Catalog(models.Model):
    _id = models.CharField(max_length=50)
    name = models.CharField(max_length=150, null=True)
    values = models.JSONField()


class Project(models.Model):
    _id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    users = models.JSONField(null=True)
    form_link = models.URLField(null=True)
