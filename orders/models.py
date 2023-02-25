from django.db import models
from accounts.models import User, Gas_Dealer


class Gas_orders(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gas_dealer = models.ForeignKey(Gas_Dealer, on_delete=models.CASCADE)
    cylinder = models.CharField(max_length=10)
    price = models.IntegerField()
    delivery = models.IntegerField()
    reference = models.CharField(max_length=50)
    confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ['user']

    def __str__(self):
        return "{} order".format(self.user)


class Cylinder_Price(models.Model):
    gas_dealer = models.ForeignKey(Gas_Dealer, on_delete=models.CASCADE)
    cylinder = models.DecimalField(decimal_places=1, max_digits=10)
    price = models.IntegerField()

    class Meta:
        ordering = ['gas_dealer']

    def __str__(self):
        return "{} {}kg NGN {}".format(self.gas_dealer, self.cylinder, self.price)


class Delivery_Fee(models.Model):
    gas_dealer = models.ForeignKey(Gas_Dealer, on_delete=models.CASCADE)
    price = models.IntegerField()

    def __str__(self):
        return "{} delivery fee".format(self.gas_dealer)
