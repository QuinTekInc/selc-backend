
from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.loginStudent),
    path('logout/', views.logoutStudent),
    path('check-enable-evaluations', views.checkEnableEvaluations),
    path('get-registered-courses/', views.getRegisteredCourses),
    path('get-questions/', views.getQuestions),
    path('submit-eval/', views.submitEvaluationData),
    path('get-course-eval/<int:cc_id>', views.getEvaluationForCourse)
]