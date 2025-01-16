from django.db import models
from accounts.models import User, Gas_Dealer
from payment.models import Payment


class Gas_orders(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gas_dealer = models.ForeignKey(Gas_Dealer, on_delete=models.CASCADE)
    cylinder = models.CharField(max_length=10)
    price = models.IntegerField()
    delivery = models.IntegerField()
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, null=True)
    dealer_confirmed = models.BooleanField(default=False)
    user_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ["user"]

    def __str__(self):
        return f"{self.user} order"
