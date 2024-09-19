from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class UserProfile(AbstractUser):
    middle_name= models.CharField(max_length=30, verbose_name='midde name', blank=True)
    position = models.CharField(max_length=30, verbose_name='position', blank=True)
    mobile_number = models.CharField(max_length=30, verbose_name='mobile number', blank=True)

class Role(models.Model):
    role= models.CharField(max_length=1000, default=None)

class UserroleMap(models.Model):
    user_id= models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role_id= models.ForeignKey(Role, on_delete=models.CASCADE)



