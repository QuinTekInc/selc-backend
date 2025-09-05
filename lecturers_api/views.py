
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.status import *

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from selc_core.models import Lecturer, Department, ClassCourse
from selc_core.models import GeneralSetting


# Create your views here.

@api_view(['POST'])
def loginLecturer(request):

    username = request.data.get('username')
    password = request.data.get('password')


    user = None

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'message': 'Incorrect username or password'})
    

    if not user.check_password(password):
        return Response({'message': 'Incorrect username or password'}, status=HTTP_401_UNAUTHORIZED)
    

    if not user.is_active:
        return Response({'message': 'Your account has been marked as inactive. Contact the administrator for support'}, status=HTTP_401_UNAUTHORIZED)
    

    lecturer = Lecturer.objects.get(user=user)    

    token, _ = Token.objects.get_or_create(user=user)


    general_setting = GeneralSetting.objects.filter().first()


    response_map = {
        'username': username,
        'auth_token': token.key,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'department': lecturer.department.department_name,
        'rating': lecturer.computeLecturerOverallAverageRating(),
        'current_semester': general_setting.current_semester,
        'enable_evaluations': general_setting.enable_evaluations
    }
    
    return Response(response_map)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logoutLecturer(request):
    logout(request)
    return Response({'message': f'{request.user.username} logged out'})



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getLecturerCourses(request):

    user: User = request.user

    lecturer = Lecturer.objects.get(user=user)

    class_courses = ClassCourse.objects.filter(lecturer=lecturer)

    return Response([class_course.toMap() for class_course in class_courses])




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getCourseQuestionnaireEvaluation(request, cc_id):

    class_course = ClassCourse.objects.get(id=cc_id)


    questionnaire_evaluationMap = class_course.getEvalDetails()

    return Response(questionnaire_evaluationMap)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getCourseCategoryEvaluation(request, cc_id):

    class_course = ClassCourse.objects.get(id=cc_id)

    category_evaluationMap = class_course.getEvalQuestionCategoryRemarks(include_questions=True)

    return Response(category_evaluationMap)





@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getLecturerRatingSummaryForCourse(request, cc_id):
    class_course = ClassCourse.objects.get(id=cc_id)
    return Response(class_course.getLecturerRatingDetails())

