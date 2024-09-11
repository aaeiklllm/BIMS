from django.db import models
from django.contrib.auth.models import User



class Role(models.Model):
    role= models.CharField(max_length=1000, default=None)

class UserroleMap(models.Model):
    user_id= models.ForeignKey(User, on_delete=models.CASCADE)
    role_id= models.ForeignKey(Role, on_delete=models.CASCADE)