from django.urls import re_path
from .consumers import (
    GasDetailsConsumerWeb,
    GasDetailsConsumerMobile,
)

gaschek_urlpatterns = [
    re_path("ws/gk/", GasDetailsConsumerWeb.as_asgi()),
    re_path("ws/gk2/", GasDetailsConsumerMobile.as_asgi()),
]
