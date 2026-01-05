
from django.urls import path
from . import views

urlpatterns = [
    path('generate-report/', views.generate_report),
    path('get-all-files/', views.get_all_files), #rename this function 'get-files/'
]