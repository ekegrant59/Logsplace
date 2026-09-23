from ast import mod
from os import name
from tabnanny import verbose
from django.db import models
from django.utils.html import mark_safe
from userauths.models import User
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
from ckeditor.fields import RichTextField

# Create your models here.
class S2(models.Model):
    name = models.TextField(null=True)
    api_url = models.URLField(null=True)
    balance_api_url = models.URLField(null=True)
    order_api_url = models.URLField(null=True)
    code_api_url = models.URLField(null=True, blank=True)
    api_key = models.TextField(null=True, blank=True)
    percentage = models.TextField(null=True, default="20")
    status = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    balance = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "USA Providers"

    def __str__(self):
        return self.name
    
class All(models.Model):
    name = models.TextField(null=True)
    api_url = models.URLField(null=True)
    balance_api_url = models.URLField(null=True)
    order_api_url = models.URLField(null=True)
    service_api_url = models.URLField(null=True, blank=True)
    code_api_url = models.URLField(null=True, blank=True)
    api_key = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    password = models.TextField(null=True, blank=True)
    percentage = models.TextField(null=True, default="20")
    status = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    balance = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "All Country Providers"

    def __str__(self):
        return self.name