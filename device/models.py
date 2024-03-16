from django.db import models
from accounts.models import User

class Gaschek_Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    choices = {
        ("on", "on"),
        ("off", "off")
    }
    device_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50, unique=True)
    alarm = models.CharField(choices=choices, max_length=10, default="off")
    call = models.CharField(choices=choices, max_length=10, default="off")
    text = models.CharField(choices=choices, max_length=10, default="off")
    indicator = models.CharField(choices=choices, max_length=10, default="off")
    cylinder = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    gas_mass = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    gas_level = models.IntegerField(default=0)
    battery_level = models.IntegerField(default=0)
    country_code = models.CharField(max_length=10, blank=True)
    phonenumber_one = models.CharField(max_length=25, blank=True)
    phonenumber_two = models.CharField(max_length=25, blank=True)
    phonenumber_three = models.CharField(max_length=25, blank=True)
    is_connected_with_device = models.BooleanField(default=False)
    device_update_time = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.device_id} Device"
    
class Leakage_History(models.Model):
    device = models.ForeignKey(
        Gaschek_Device, on_delete=models.CASCADE)
    action = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.device)
