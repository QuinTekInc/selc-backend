

from django.urls import path  
from . import views


urlpatterns = [
    path('login/', views.loginLecturer),
    path('logout/', views.logout)
]