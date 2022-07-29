from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    c_name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='photos/%y/%m/%d/', null=True)
    quantity = models.IntegerField(null=True)

class Article(models.Model):
    name = models.CharField(max_length=50)
    category = models.ManyToManyField(Category)
    prix = models.IntegerField()
    description = models.TextField(max_length=300, null=True)
    taille = models.CharField(max_length=50, null=True)
    color = models.CharField(max_length=50, null=True)
    quantity = models.IntegerField()
    photo = models.ImageField(upload_to='photos/%y/%m/%d/')

    def __str__(self):
        return self.name

class User_Detail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=50)
    
class Panier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)


class Command(models.Model):
    type_of_payement = models.CharField(max_length=50)
    price = models.IntegerField()
    panier = models.OneToOneField(Panier, on_delete=models.CASCADE, null=True)

class ArticleInPanier(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, null=True)
    taille = models.CharField(max_length=50, null=True)
    quantity = models.IntegerField(null=True)


class Favorit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    article = models.ManyToManyField(Article)