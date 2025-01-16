from django.urls import re_path
from .consumers import GasDealerOrdersConsumer

orders_urlpatterns = [
    re_path("ws_order/get_dealer_orders/", GasDealerOrdersConsumer.as_asgi())
]
