"""
ASGI config for selc_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import admin_api.ws_routing
import lecturers_api.ws_routing



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selc_backend.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AuthMiddlewareStack( 
        URLRouter(
            admin_api.ws_routing.websocket_urlpatterns +
            lecturers_api.ws_routing.websocket_urlpatterns
        )
    )
})
