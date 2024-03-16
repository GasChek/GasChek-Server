from django.urls import re_path
from .consumers import (
                        GasDetailsConsumer,
                        GasDetailsConsumerMobileApp,
                        # GasDetailsConsumerEmulation,
                        )
gaschek_urlpatterns = [
    re_path('ws/gk/', GasDetailsConsumer.as_asgi()),
    re_path('ws/gk2/', GasDetailsConsumerMobileApp.as_asgi()),
    # re_path('ws/gk/', GasDetailsConsumerEmulation.as_asgi()),
]
