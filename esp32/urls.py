from django.urls import path
from .views import (Update_esp32_details,
                    Get_gaschek_details,
                    Report_gas_leakage,
                    Get_Leakage_Notification_Details)

urlpatterns = [
    path('update_details/', Update_esp32_details.as_view()),
    path('get_details/', Get_gaschek_details.as_view()),
    path('leakage/', Report_gas_leakage.as_view()),
    path('leakage_notification/', Get_Leakage_Notification_Details.as_view()),
    # path('reset/', Reset_GasChek_device.as_view())
]
