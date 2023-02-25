from django.urls import re_path
# from .consumers import (GasDetailsConsumer, 
#                         GasDetailsDeviceConsumer, 
#                         SendDeviceDetailsConsumer,
#                         GasLeakageNotificationConsumer)
# from orders.consumers import GasDealerOrdersConsumer
# from .asyncconsumers import (GasDetailsConsumer, 
#                             ToggleGasDetailsConsumer,
#                             GasDetailsDeviceConsumer, 
#                             SendDeviceDetailsConsumer,
#                             GasLeakageNotificationConsumer)
# from orders.consumers import GasDealerOrdersConsumer

from .async_sync_consumers import (GasDetailsConsumer, 
                            ToggleGasDetailsConsumer,
                            GasDetailsDeviceConsumer, 
                            SendDeviceDetailsConsumer,
                            GasLeakageNotificationConsumer)
from orders.consumers import GasDealerOrdersConsumer
urlpatterns = [
    re_path('ws/get_details/', GasDetailsConsumer.as_asgi()),
    re_path('ws/toggle_details/', ToggleGasDetailsConsumer.as_asgi()),
    re_path('ws/get_device_details/', GasDetailsDeviceConsumer.as_asgi()),
    re_path('ws/send_device_details/', SendDeviceDetailsConsumer.as_asgi()),
\
    re_path('ws_order/get_dealer_orders/', GasDealerOrdersConsumer.as_asgi()),
    re_path('ws/get_gas_leakage/', GasLeakageNotificationConsumer.as_asgi())
]
