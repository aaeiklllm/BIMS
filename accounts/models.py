from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class UserProfile(AbstractUser):
    middle_name= models.CharField(max_length=150, verbose_name='midde name', null=True, blank=True)
    position = models.CharField(max_length=150, verbose_name='position', blank=True)
    unit = models.CharField(max_length=150, verbose_name='unit', null=True, blank=True)
    mobile_number = models.CharField(max_length=30, verbose_name='mobile number', blank=True)
    deletion_requested = models.BooleanField(default=False, verbose_name='Deletion Requested')
    deletion_approved = models.BooleanField(default=False, verbose_name='Deletion Approved')

class Role(models.Model):
    role= models.CharField(max_length=150, default=None)

class UserroleMap(models.Model):
    user_id= models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role_id= models.ForeignKey(Role, on_delete=models.CASCADE)

class PasswordResetCode(models.Model):
    code = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.code


