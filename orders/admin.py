from django.contrib import admin
from .models import Gas_orders
from accounts.models import Cylinder_Price, Delivery_Fee

# Register your models here.
admin.site.register(Gas_orders)
admin.site.register(Cylinder_Price)
admin.site.register(Delivery_Fee)
