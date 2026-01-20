"""
ASGI config for selc_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selc_backend.settings')

import django

django.setup()


from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from  admin_api.routing import websocket_urlpatterns as admin_urlpatterns
from lecturers_api.routing import websocket_urlpatterns as lecturer_urlpatterns


websocket_routes = admin_urlpatterns + lecturer_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': URLRouter(websocket_routes) 
})
