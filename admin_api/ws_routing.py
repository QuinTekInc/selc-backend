
from django.urls import re_path 
from .consumers import DashboardGraphConsumer

websocket_urlpatterns = [ 
    re_path(r'ws/selc-admin/dashboard/graph-data/$', DashboardGraphConsumer.as_asgi()),
]


