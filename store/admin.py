from django.contrib import admin
from .models import Slider, Product, Category, Author


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_per_page = 20

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 20

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_per_page = 20

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_per_page = 20