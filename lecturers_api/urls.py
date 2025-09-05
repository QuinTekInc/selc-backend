

from django.urls import path  
from . import views


urlpatterns = [
    path('login/', views.loginLecturer),
    path('logout/', views.logoutLecturer),
    path('get-courses/', views.getLecturerCourses),
    path('get-course-eval/<int:cc_id>', views.getCourseQuestionnaireEvaluation),
    path('get-course-cat-eval/<int:cc_id>', views.getCourseCategoryEvaluation),
    path('get-course-lrating-eval/<int:cc_id>', views.getLecturerRatingSummaryForCourse)
]