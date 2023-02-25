from django.urls import re_path
from .consumers import GasDealerOrdersConsumer

urlpatterns = [
    re_path('ws_order/get_dealer_orders/', GasDealerOrdersConsumer.as_asgi())
]
