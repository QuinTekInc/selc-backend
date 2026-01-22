
from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/admin-dashboard/$', consumers.AdminDashboardGraphConsumer.as_asgi()),
    re_path(r'ws/lecturer-dashboard/$', consumers.LecturerDashboardGraphDataConsumer.as_asgi()),
    re_path(r'ws/test/$', consumers.TestConsumer.as_asgi())
]