from django.db import models
from main.models import *
from users.models import *


class ImportProduct(models.Model):
    buy_price = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - {self.buy_price}'


class Sale(models.Model):
    quantity = models.FloatField(default=0)
    total_price = models.FloatField(default=0)
    paid_price = models.FloatField(default=0)
    debt_price = models.FloatField(default=0)

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - {self.branch.name} - {self.client.name} - {self.debt_price}'


class PayDebt(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    description = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
