from django.db import models
from accounts.models import Gaschek_Device


# Create your models here.
class Gas_Leakage(models.Model):
    gaschek_device = models.ForeignKey(
        Gaschek_Device, on_delete=models.CASCADE)
    action = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.gaschek_device)
