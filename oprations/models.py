from django.db import models
from store.models import Product

class PaymentMethod(models.IntegerChoices):
    PAYPAL = 1, 'PayPal'
    STRIPE = 2, 'Stripe'

class TransactionStatus(models.IntegerChoices):
    PENDING = 0, 'Pending'
    COMPLETED = 1, 'Completed'
    CANCELED = 2, 'Canceled'


class Transaction(models.Model):
    session = models.CharField(max_length=255)
    items = models.JSONField(default=dict)
    customer = models.JSONField(default=dict)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    paymeny_method = models.IntegerField(choices=PaymentMethod.choices, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def customer_name(self):
        return self.customer['first_name'] + ' ' + self.customer['last_name']
    
    @property
    def customer_email(self):
        return self.customer['email']




class Order(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.pk)

    
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
