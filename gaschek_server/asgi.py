"""
ASGI config for gaschek_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

# Must do this for daphne to work 
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaschek_server.settings')
django.setup()
# Must do this for daphne to work 

from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import orders.routing
import esp32.routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                esp32.routing.gaschek_urlpatterns +
                orders.routing.orders_urlpatterns
            )
        )
    )
})
