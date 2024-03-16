from django.contrib import admin
from .models import User, Gas_Dealer, Token, Abandoned_Subaccounts
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'created_at', 'updated_at']
    search_fields = ['id', 'email', 'first_name', 'last_name']
    
admin.site.register(User, UserAdmin)
admin.site.register(Gas_Dealer)
admin.site.register(Token)
admin.site.register(Abandoned_Subaccounts)

