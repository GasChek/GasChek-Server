from django.urls import path
from .views import Report_gas_leakage, Update_esp32_details, Get_gaschek_details_SSE

urlpatterns = [
    path('leakage/', Report_gas_leakage.as_view()),
    path('update_device/', Update_esp32_details.as_view()),
    path('get_device/', Get_gaschek_details_SSE.as_view()),
]
