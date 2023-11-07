from django.urls import re_path
from .consumers import (GasDetailsConsumer,
                        ToggleDetailsConsumer,
                        GasDetailsDeviceConsumer,
                        SendDeviceDetailsConsumer,
                        )
gaschek_urlpatterns = [
    re_path('ws/get_details/', GasDetailsConsumer.as_asgi()),
    re_path('ws/toggle_details/', ToggleDetailsConsumer.as_asgi()),
    re_path('ws/get_device_details/', GasDetailsDeviceConsumer.as_asgi()),
    re_path('ws/send_device_details/', SendDeviceDetailsConsumer.as_asgi()),
]
