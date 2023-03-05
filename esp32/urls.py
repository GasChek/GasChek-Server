from django.urls import path
from .views import Report_gas_leakage

urlpatterns = [
    path('leakage/', Report_gas_leakage.as_view()),
]
