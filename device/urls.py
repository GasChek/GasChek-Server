from django.urls import path
from .views import (ConnectDeviceAPI, 
                    Report_leakage, 
                    # Update_device_details, 
                    # Get_gaschek_details_SSE
                    )

urlpatterns = [
    path('connect-device/', ConnectDeviceAPI.as_view()),    
    path('leakage/', Report_leakage.as_view()),
    # path('update_device/', Update_device_details.as_view()),
    # path('get_device/', Get_gaschek_details_SSE.as_view()),
]
