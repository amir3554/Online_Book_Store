from django.db import models
from django.contrib.sessions.models import Session
from mystore_project import settings


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(null=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=255)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    short_description = models.TextField(max_length=255, null=True)
    description = models.TextField(null=True)
    price = models.FloatField()
    stock = models.PositiveIntegerField(null=True)
    image = models.ImageField(upload_to='products_images/', null=True)
    pdf_file = models.FileField(upload_to='products_files/')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)

    @property
    def pdf_file_url(self):
        return settings.MEDIA_ROOT + self.pdf_file.url
    
    def __str__(self) -> str:
        return self.name


class Slider(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(max_length=500)
    image = models.ImageField(null=True)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class Cart(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    items = models.JSONField(default=True)
