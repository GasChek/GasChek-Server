from django.urls import path
from .views import (LoginAPI,
                    UserViewAPI, UpdateUserAPI,
                    AccountViewAPI, CreateGasDealerAPI,
                    Verify_Otp, Resend_Otp, Dealer_LoginAPI,
                    GasDealerViewAPI, GetGasDealerAPI,
                    Update_GasDealer_details)

urlpatterns = [
    path('get_account_type/', AccountViewAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('get_user/', UserViewAPI.as_view()),
    path('update_user/', UpdateUserAPI.as_view()),

    path('create_dealer/', CreateGasDealerAPI.as_view()),
    path('otp/', Verify_Otp.as_view()),
    path('resend-otp/', Resend_Otp.as_view()),
    path('dealer_login/', Dealer_LoginAPI.as_view()),
    path('get_dealer/', GetGasDealerAPI.as_view()),
    path('get_dealer_view/', GasDealerViewAPI.as_view()),
    path('update_gas_dealer/', Update_GasDealer_details.as_view()),
]
