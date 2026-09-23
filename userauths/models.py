from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from shortuuid.django_fields import ShortUUIDField

class User(AbstractUser):
    unique_id = ShortUUIDField(length=25, max_length=40, null=True, alphabet="adft6543kb")
    username = models.CharField(unique=True, null=True, blank=True, max_length=100)
    email = models.EmailField(unique=True, null=False)
    first_name = models.CharField(max_length=1000, null=True)
    last_name = models.CharField(max_length=1000, null=True)
    bio = models.CharField(max_length=1000, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=100000, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email}"
    
    class Meta:
        app_label = 'userauths'
        # Ensure that the reverse accessors have unique names
        unique_together = ('email', 'username')

    # Override the groups and user_permissions fields to use custom related_name
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Unique related_name for groups
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Unique related_name for user permissions
        blank=True,
        help_text='Specific permissions for this user.'
    )
