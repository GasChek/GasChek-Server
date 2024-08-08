from django.contrib import admin
from .models import Leakage_History, Gaschek_Device


class Gaschek_DeviceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "alarm",
        "call",
        "text",
        "indicator",
        "cylinder",
        "gas_mass",
        "gas_level",
        "battery_level",
    ]
    search_fields = [
        "id",
        "alarm",
        "call",
        "text",
        "indicator",
        "cylinder",
        "gas_mass",
        "gas_level",
        "battery_level",
    ]


admin.site.register(Gaschek_Device, Gaschek_DeviceAdmin)
admin.site.register(Leakage_History)
