from django.urls import path
from .views import PaymentAPI

urlpatterns = [
    path('payment_api/', PaymentAPI.as_view()),
]
