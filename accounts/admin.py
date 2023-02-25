from django.contrib import admin
from .models import User, Gas_Dealer, Token, Gaschek_Device
# Register your models here.

admin.site.register(User)
admin.site.register(Gas_Dealer)
admin.site.register(Gaschek_Device)
admin.site.register(Token)
