

from django.urls import path  
from . import views


urlpatterns = [
    path('login/', views.loginLecturer),
    path('logout/', views.logoutLecturer),
    path('get-courses/', views.getLecturerCourses),
    path('get-course-eval/<int:cc_id>', views.getCourseQuestionnaireEvaluation),
    path('get-course-lrating-eval/<int:cc_id>', views.getLecturerRatingSummaryForCourse),
    path('get-course-eval-suggestions/<int:cc_id>', views.getEvaluationSuggestions),
    path('class-course-detail-by-program/<int:cc_id>', views.getCCDetailsByProgram),
]