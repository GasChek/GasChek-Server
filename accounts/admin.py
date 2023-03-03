from django.contrib import admin
from .models import User, Gas_Dealer, Token, Gaschek_Device, Abandoned_Subaccounts
# Register your models here.

admin.site.register(User)
admin.site.register(Gas_Dealer)
admin.site.register(Gaschek_Device)
admin.site.register(Token)
admin.site.register(Abandoned_Subaccounts)

