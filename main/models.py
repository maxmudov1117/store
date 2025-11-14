from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=255)
    info = models.TextField()

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(default=0, blank=True, null=True)
    quantity = models.FloatField(default=0)
    unit = models.CharField(max_length=255)

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=255)
    shop_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=23)
    address = models.CharField(max_length=255)
    debt = models.FloatField(default=0)

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
