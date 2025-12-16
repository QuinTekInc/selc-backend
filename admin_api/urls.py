
from django.urls import path
from . import views

urlpatterns = [

    #todo: superuser stuff.
    path('all-users/', views.getListOfUsers),
    path('create-user/', views.createUser),
    path('su-update-user/', views.superuser_UpdateUser),


    #todo: for user authentication
    path('login/', views.loginAdmin),
    path('logout/', views.logoutAdmin),
    path('update-account-info/', views.updateAccountInfo),

    #todo: dashboard urls
    path('general-current-stats/', views.generalCurrentStatistics),
    path('lecturers-ratings-rank/', views.getLecturersRatings),
    path('courses-ratings-rank/', views.getCourseRatings),


    #todo: general setting urls
    path('get-general-settings/',views.getGeneralSetting),
    path('update-general-settings/', views.updateSetting),

    path('get-class-courses/', views.getClassCourses),
    path('update-class-course/', views.updateClassCourse),
    
    path('get-all-current-class-courses/', views.getCurrentClassCourses),
                                        #todo: change to sentiment summary
    path('get-all-current-class-courses-sentiments/', views.getCurrentClassCourseSentimentSummary),
    path('get-all-current-class-courses-categories-summary/', views.getCurrentClassCoursesCategoriesSummary),

    
    path('departments/', views.getDepartments),
    path('get-department-class-courses/<int:department_id>', views.getDepartmentClassCourses),
    
    path('lecturers/', views.getLecturers),
    path('lecturer-info/<str:username>', views.getLecturerInformation),
    path('overall-lrating-summary/<str:username>', views.getOverallLecturerRatingSummary),
    path('yearly-average-lrating-summary/<str:username>', views.getYearlyLecturerRatingSummary),
    path('course-info/<str:course_code>', views.getCourseInformation),

    #todo: ClassCourse evaluation information
    path('class-course-eval-summary/<int:cc_id>', views.getClassCourseEvalSummary),
    path('eval-question-category-remark/<int:cc_id>', views.getCourseEvalCategoryRemarks),
    path('eval-suggestions/<int:cc_id>', views.getEvaluationSuggestions),
    path('eval-lrating-summary/<int:cc_id>', views.getEvalLecturerRatingSummary),
    

    path('questions-and-categories/', views.getQuestionsAndCategories),

    #todo: requstionnaire categories
    path('add-category/', views.addCategory),
    path('update-category/<int:category_id>/', views.updateCategory),
    path('delete-category/<int:category_id>/', views.deleteCategory),


    #todo: questionnaires and the questionnaire
    path('add-questionnaire/', views.addQuestionnaire),
    path('delete-questionnaire/', views.updateQuestionnaire),
    path('update-questionnaire/', views.updateQuestionnaire),


    path('add-course/', views.addCourse),


    path('courses/', views.getCourses)
]
