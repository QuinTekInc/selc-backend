
from django.urls import path
from . import views

urlpatterns = [
    path('file-path/', views.generate_report),
    path('all-files/', views.get_all_files)
]