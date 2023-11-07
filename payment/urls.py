from django.urls import path
from .views import PaymentAPI, VerifyPayment_Hook

urlpatterns = [
    path('payment_api/', PaymentAPI.as_view()),
    path('payment_hook/', VerifyPayment_Hook.as_view()),
]
