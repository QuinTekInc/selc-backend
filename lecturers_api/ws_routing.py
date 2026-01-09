
from django.urls import re_path 
from .consumers import LDashboardGraphDataConsumer 

websocket_urlpatterns = [
    re_path(r'ws/selc-lecturer/dashboard/graph-data/$', LDashboardGraphDataConsumer.as_asgi()),
]