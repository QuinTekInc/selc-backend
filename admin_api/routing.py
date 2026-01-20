
from django.urls import re_path 
from .consumers import DashboardGraphConsumer, TestConsumer

websocket_urlpatterns = [ 
    re_path(r'ws/selc-admin/dashboard/token=(?P<token>[^/]+)/', DashboardGraphConsumer.as_asgi()),
    re_path(r'ws/test/', TestConsumer.as_asgi())
]


