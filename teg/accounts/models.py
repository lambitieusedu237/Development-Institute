from django.db import models

# Create your models here.

class Register(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255, null=True )
    email = models.EmailField(max_length=255) 
    gender = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255)
    password2 = models.CharField(max_length=255)

class Login(models.Model):
    user_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
