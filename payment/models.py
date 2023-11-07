from django.db import models
from accounts.models import User, Gas_Dealer, Cylinder_Price

# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gas_dealer = models.ForeignKey(Gas_Dealer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_for = models.ForeignKey(Cylinder_Price, on_delete=models.CASCADE)
    delivery = models.IntegerField()
    reference = models.CharField(max_length=50)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.payment_for)
