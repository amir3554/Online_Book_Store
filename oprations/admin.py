from django.contrib import admin
from django.http import HttpRequest
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'amount', 'items', 'payment_method', 'created_at']
    list_per_page = 20
    list_select_related = ['transaction']

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
    
    def amount(self, obj):
        return obj.transaction.amount
    
    def items(self, obj):
        return len(obj.transaction.items)
    
    def email(self, obj):
        return obj.transaction.customer_email
    
    def payment_method(self, obj):
        return obj.transaction.get_payment_method_display()