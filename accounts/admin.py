from django.contrib import admin
from .models import User, Gas_Dealer, Token, Gaschek_Device, Abandoned_Subaccounts
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'usernames', 'email', 'first_name', 'last_name', 'created_at', 'updated_at']
    search_fields = ['id', 'email', 'first_name', 'last_name']
    
class Gaschek_DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','alarm', 'call', 
                    'text', 'indicator', 'cylinder', 'gas_mass', 'gas_level', 'battery_level']
    search_fields = ['id', 'alarm', 'call',
                    'text', 'indicator', 'cylinder', 'gas_mass', 'gas_level', 'battery_level']

admin.site.register(User, UserAdmin)
admin.site.register(Gas_Dealer)
admin.site.register(Gaschek_Device, Gaschek_DeviceAdmin)
admin.site.register(Token)
admin.site.register(Abandoned_Subaccounts)

