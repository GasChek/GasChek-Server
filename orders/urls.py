from django.urls import path
from .views import (AllGasDealersAPI,
                    Create_Cylinder_Price,
                    Get_Cylinder_Price,
                    Get_orders,
                    GasDealer_SearchAPI,
                    Confirm_OrderAPI,
                    Create_Delivery_Fee,
                    Get_Delivery_Fee
                    )

urlpatterns = [
    path('gasdealers/', AllGasDealersAPI.as_view()),
    path('create_cylinder_price/', Create_Cylinder_Price.as_view()),
    path('cylinder_price/', Get_Cylinder_Price.as_view()),
    path('create_delivery_fee/', Create_Delivery_Fee.as_view()),
    path('delivery_fee/', Get_Delivery_Fee.as_view()),
    path('get_orders/', Get_orders.as_view()),
    path('confirm_order/', Confirm_OrderAPI.as_view()),
    path('dealer_search/', GasDealer_SearchAPI.as_view())
]
