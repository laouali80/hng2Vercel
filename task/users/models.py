from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

class User(AbstractUser):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.CharField(max_length=15, blank=False, null=False)
    lastName = models.CharField(max_length=15, blank=False, null=False)
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    
    organisations = models.ManyToManyField('Organisation', related_name='users')


    def __str__(self):
        return self.email

class Organisation(models.Model):
    orgId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, blank=False, null=False, )
    description = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name
    
    
