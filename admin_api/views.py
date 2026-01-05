
import datetime
from django.contrib.auth.models import User, Group, GroupManager
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import *
from selc_core.models import *
from . import utils

from .utils import createUserAccountDict, buildParamLecturerMap, buildCourseRateMap
from .decorators import requires_superuser, requires_roles




@api_view(['GET'])
@requires_superuser
def getListOfUsers(request):

    # users = User.objects.filter(
    #     Q(groups__name='superuser') | Q(groups__name='admin') | Q(is_superuser=True)).distinct()

    users = User.objects.all()

    users_list_dict: list[dict] = []

    for user in users:

        user_map = createUserAccountDict(user)

        users_list_dict.append(user_map)


    return Response(users_list_dict)





@api_view(['POST'])
@requires_superuser
def createUser(request):

    request_data = request.data

    username = request_data['username']

    if User.objects.filter(username=username).exists():
        return Response('Username already exist.')

    first_name = request_data['first_name']
    last_name = request_data['last_name']

    email = request_data['email']

    password = request_data['password']

    group_name = request_data['role']

    #create the actual user object.
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    if group_name == 'superuser':
        user.is_superuser = True
    else: 
        user.is_staff = True

    user.save()


    group = Group.objects.get(name=group_name)
    user.groups.add(group)

    return Response({'message': f'User, {username},  has been succesfully created.'})






@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@requires_superuser
def superuser_UpdateUser(request,):

    request_data = request.data

    username = request_data['username']

    user: User = User.objects.get(username=username)

    is_active_in_data = 'is_active' in request_data

    
    if is_active_in_data:
        user.is_active = request_data['is_active']

        if request_data['is_active']:
            n_title = 'Account Suspended'
            n_message = 'You account has been marked as inactive.'
        else: 
            n_title = 'Account activate'
            n_message = 'You account has been reactivated.'

        #add the notification to the user.
        notification = Notification.objects.create(user=user, title=n_title, message=n_message)
        notification.save()
        pass

    if 'role' in request_data:
        user.groups.clear() #delete the current user group.

        group = Group.objects.get(name=request_data['role'])
        user.groups.add(group)


        if request_data['role'].lower() == 'superuser':
            user.is_superuser = True


        Notification.objects.create(  
            user=user, title = 'Roles and Permission', 
            message = f'Your role has been changed to {request_data["role"]}'
        ).save()

        pass

    user.save()


    #todo: sending e-mail to the user based on updates that has been applied (either role update or active status update)

    return Response({'message': f'User, {username}, account has been disabled'})




# Create your views here.
# when an admin want's to login
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def loginAdmin(request):

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'message': 'Username and password are required.'}, status=HTTP_401_UNAUTHORIZED)

    print('This place has been passed')
    

    user = None

    try:
        user = User.objects.get(username=username)
        
        if not user.check_password(password):
            return Response({'message': 'Invalid username or password.'}, status=HTTP_401_UNAUTHORIZED)
        
    except User.DoesNotExist:
        return Response({'message': 'Invalid username or password.'}, status=HTTP_401_UNAUTHORIZED)


    if not user.is_active:
        return Response({'message': 'Your account has been marked as inactive. Contact the superuser for support.'}, status=HTTP_403_FORBIDDEN)


    login(request, user)

    # Create or get token
    token, _ = Token.objects.get_or_create(user=user)

    user_dict = createUserAccountDict(user, auth_token=token)  # Ensure token.key, not token object

    #add the general setting to the user dict
    general_setting = GeneralSetting.objects.first()
    user_dict['general_setting'] = general_setting.toMap()


    return Response(user_dict, status=HTTP_200_OK)





@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logoutAdmin(request):
    user: User = request.user
    logout(request)
    return Response({'message': f'{user.username}, has logged out.'})





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateAccountInfo(request):
    
    user: User = request.user

    request_data = request.data

    if 'old_password' in request_data and 'new_password' in request_data:

        #check if the old_password is equal to the password in the current user object.
        is_correct_password: bool = user.check_password(request_data['old_password'])

        if not is_correct_password:
            return Response({'message': 'The password you entered is incorrect. Please try again'}, status=HTTP_406_NOT_ACCEPTABLE)
        
        user.set_password(request_data['new_password'])
        pass

    if 'email' in request_data:
        user.email = request_data['email']

    if 'last_name' in request_data:
        user.last_name = request_data['last_name']

    if 'first_name' in request_data:
        user.first_name = request_data['first_name']


    user.save()

    token = Token.objects.get(user=user)

    return Response(createUserAccountDict(user, auth_token=token))





@api_view(['GET'])
def getGeneralSetting(request):
    return Response(GeneralSetting.objects.all().first().toMap())




@api_view(['POST'])
@requires_superuser
def updateSetting(request):
    general_setting = GeneralSetting.objects.all().first()
    general_setting.current_semester = request.data.get('current_semester')
    general_setting.disable_evaluations = request.data.get('disable_evaluations')

    general_setting.save()

    return Response(general_setting.toMap())





@api_view(['GET'])
#@requires_roles(['superuser', 'admin'])
def generalCurrentStatistics(request):


    current_year = datetime.datetime.now().year 
    current_semester = GeneralSetting.objects.first().current_semester

    lecturers_count = Lecturer.objects.count()

    courses_count = ClassCourse.objects.count()

    questions_count = Questionnaire.objects.count()

    evaluations_count = StudentClass.countEvaluatedCoursesFor(current_year, current_semester)

    suggestions_count = EvaluationSuggestion.countClassCoursesFor(current_year, current_semester)
                                    

    return Response({
        'lecturers_count': lecturers_count,
        'courses_count': courses_count,
        'questions_count' : questions_count,
        'current_semester': current_semester, 
        'evaluations_count': evaluations_count,
        'suggestions_count': suggestions_count
    })





@api_view(['GET'])
def getDepartments(request):
    departments = Department.objects.all()
    return Response([department.toMap() for department in departments])


#caching needs to be implemented here.
@authentication_classes([TokenAuthentication])
@api_view(['GET'])
def getClassCourses(request):
    class_courses = ClassCourse.objects.all().order_by('year', 'semester',)
    return Response([cc.toMap() for cc in class_courses])


@api_view(['POST'])
def updateClassCourse(request, cc_id):
    request_data = request.data

    cc_id = request_data.get('cc_id', None)

    accepting_response = request_data.get('is_accepting_response', None)

    if cc_id is None or accepting_response is None:
        return Response({"message": 'Bad request made'}, status=HTTP_400_BAD_REQUEST)
    

    class_course = ClassCourse.objects.get(id=cc_id)
    class_course.is_accepting_response = accepting_response
    class_course.save()

    return Response({'message': 'ClassCourse updated'}, status=HTTP_200_OK)



@api_view(['GET'])
def getDepartmentClassCourses(request, department_id):

    general_setting = GeneralSetting.objects.all().first()

    department = Department.objects.get(id=department_id)


    #lecturers in the department
    lecturers = Lecturer.objects.filter(department=department)

    #class_courses for this department
    class_courses = ClassCourse.objects.filter(lecturer__in=lecturers)

    return Response([class_course.toMap() for class_course in class_courses])





@api_view(['GET'])
def getLecturers(request):

    lecturers = Lecturer.objects.all()

    lecturers_list = [lecturer.toMap() for lecturer in lecturers]

    return Response(lecturers_list)







@api_view(['GET'])
def getCurrentClassCourses(request):
    general_setting = GeneralSetting.objects.all().first()

    class_courses = ClassCourse.objects.filter(semester=general_setting.current_semester, year=datetime.datetime.now().year)

    class_courses_map_list: list[dict] = [class_course.toMap() for class_course in class_courses]
    
    return Response(class_courses_map_list)



#categories scores for the lecturers for the current year and academic semester
@api_view(['GET'])
def getCurrentClassCoursesCategoriesSummary(request):

    general_setting = GeneralSetting.objects.all().first()

    class_courses = ClassCourse.objects.filter(semester=general_setting.current_semester, year=datetime.datetime.now().year)

    lecturers_eval_categories_list: list[dict] = []

    for class_course in class_courses:
        category_dict = {
            'lecturer': class_course.lecturer.getFullName(),
            'department': class_course.lecturer.department.department_name, 
            'course': class_course.course.toMap(),
            'categories_summary': class_course.getEvalQuestionCategoryRemarks(),
        }

        lecturers_eval_categories_list.append(category_dict)
        pass


    return Response(lecturers_eval_categories_list)





@api_view(['GET'])
def getCurrentClassCourseSentimentSummary(request):

    general_setting = GeneralSetting.objects.all().first()

    class_courses = ClassCourse.objects.filter(semester=general_setting.current_semester, year=datetime.datetime.now().year)

    sentiments_map_list: list[dict] = []

    for class_course in class_courses:

        sentiment_summary = {
            'lecturer': class_course.lecturer.getFullName(),
            'course': class_course.course.toMap(),
            'sentiment_summary': class_course.getEvalSuggestions()['sentiment_summary'] #todo: optimize this line of code later
        }

        sentiments_map_list.append(sentiment_summary)
        pass

    return Response(sentiments_map_list)





@api_view(['GET'])
def getLecturerInformation(request, username):

    user = User.objects.get(username=username)

    lecturer = Lecturer.objects.get(user=user)

    #all the courses taught by the lecturer
    class_courses = ClassCourse.objects.filter(lecturer=lecturer)

    class_courses_dict: list[dict] = [cc.toMap() for cc in class_courses]

    return Response(class_courses_dict)




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getOverallLecturerRatingSummary(request, username):

    user = User.objects.get(username=username)
    lecturer = Lecturer.objects.get(user=user)

    return Response(lecturer.getOverallRatingSummary())




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getYearlyLecturerRatingSummary(request, username):

    user = User.objects.get(username=username)
    lecturer = Lecturer.objects.get(user=user)

    return Response(lecturer.getYearlyAverageRatingSummary())





@api_view(['GET'])
def getCourseInfo(request, course_code: str):
    course = Course.objects.get(course_code=course_code)
    return Response(course.courseInfo())





@api_view(['GET'])
def getQuestionsAndCategories(request):

    categories = QuestionCategory.objects.all()

    categories_dict: list[dict] = [cat.toMap() for cat in categories]
    

    questions = Questionnaire.objects.all()
    questions_dict: list[dict] = [question.toMap() for question in questions]
    

    return Response({'categories': categories_dict, 'questions': questions_dict})





@api_view(['POST'])
def addCategory(request):

    category_name = request.data.get('category_name')

    category = QuestionCategory.objects.create(cat_name=category_name)
    category.save()

    return Response(category.toMap())





@api_view(['POST'])
def updateCategory(request, category_id):

    category_name = request.data.get('category_name')

    category = QuestionCategory.objects.get(cat_id=category_id)
    category.cat_name = category_name
    category.save()

    return Response(category.toMap())





@api_view(['POST'])
@requires_superuser
def deleteCategory(request, category_id):

    category = QuestionCategory.objects.get(cat_id=category_id)

    #the new category id to replace the ones to be deleted.
    replacement_category_id = request.data.get('replacement_category_id')
    

    if replacement_category_id:

        replacement_category = QuestionCategory.objects.get(cat_id=replacement_category_id)
        
        #TODO: Implement a function to replace questions under a deleted categories with a new category.
        #get the questions from the category we want to delete
        category_questions = Questionnaire.obejcts.filter(category=category)

        for questionnaire in category_questions:
            questionnaire.category = replacement_category
            questionnaire.save()

        pass


    category.delete()

    return Response({'message': f'{category_id} has been deleted.'})






@api_view(['POST'])
@requires_superuser
def addQuestionnaire(request):

    request_data = request.data

    question = Questionnaire.objects.create(
        question=request_data['question'],
        answer_type=request_data['answer_type'],
        category=QuestionCategory.objects.get(cat_id=request_data['category'])
    )

    question.save()

    return Response(question.toMap())





@api_view(['DELETE'])
@requires_superuser
def deleteQuestionnaire(request, question_id: int):

    question = Questionnaire.objects.get(id=question_id)

    question.delete()

    return Response({'message': f'Questionnaire, {question_id}, has been deleted'})





@api_view(['POST'])
@requires_superuser
def updateQuestionnaire(request, question_id: int):

    request_data = request.data

    new_answer_type = request_data['answer_type']


    question: Questionnaire = Questionnaire.objects.get(id=question_id)

    old_answer_type = question.answer_type

    question.answer_type = request_data['answer_type']
    question.question = request_data['question']
    question.category = QuestionCategory.objects.get(cat_id=request_data['category'])


    if new_answer_type == old_answer_type:
        question.save()
        return Response(question.toMap())



    #evaluation questions that corresponds to this questionnaire
    evaluations = Evaluation.objects.filter(question=question)

    for evaluation in evaluations:
        evaluation.answer = request_data['replacement_answer']
        evaluation.save()

    question.save()

    return Response(question.toMap())




@api_view(['POST'])
@requires_superuser
def addCourse(request):

    request_data = request.data

    course = Course.objects.create(course_code=request_data['course_code'], title=request_data['course_title'])

    course.save()

    return Response(course.toMap())





@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def getClassCourseEvalSummary(request, cc_id):
    
    #get the all the class courses related to that course
    class_course = ClassCourse.objects.get(id=cc_id)
    
    #generate the evaluation summary dictionary
    #eval_answer_map = utils.groupQuestionAnswerSummary([class_course])
    eval_answer_map = class_course.getEvalDetails()

    #todo: get the evaluation suggestions for the course.
    return Response(eval_answer_map)




@api_view(['GET'])
def getCourseEvalCategoryRemarks(request, cc_id):
    class_course = ClassCourse.objects.get(id=cc_id)
    return Response(class_course.getEvalQuestionCategoryRemarks())




@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def getEvaluationSuggestions(request, cc_id):

    class_course = ClassCourse.objects.get(id=cc_id)

    # lecturer_ratings = LecturerRating.objects.filter(class_course=class_course)


    # suggestions_map: list[dict] = []

    # for l_rating in lecturer_ratings:
    #     student = l_rating.student
    #     suggestion = EvaluationSuggestion.objects.filter(student=student, class_course=class_course)

    #     _suggestion = ''
    #     if suggestion.exists():
    #         _suggestion = suggestion.first().suggestion
        
    #     suggestions_map.append({'rating': l_rating.rating, 'suggestion': _suggestion})

    

    return Response(class_course.getEvalSuggestions())



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def getEvalLecturerRatingSummary(request, cc_id):
    class_course = ClassCourse.objects.get(id=cc_id)
    return Response(class_course.getLecturerRatingDetails())





#todo: courses will be obtained by an api to the "I.T directorate's" database.
@api_view(['GET'])
def getCourses(request):
    courses = Course.objects.all()
    return Response([course.toMap() for course in courses])








@api_view(['GET', 'POST'])
def getLecturersRatings(request):

    lecturers = Lecturer.objects.all()

    if request.method == 'GET':

        lecturers_map_list = [
            buildParamLecturerMap(lecturer, ClassCourse.objects.filter(lecturer=lecturer))
            for lecturer in lecturers 
        ]

        lecturers_map_list = sorted(
            lecturers_map_list, 
            key=lambda rating_map: rating_map['parameter_rating'], reverse=True)

        return Response(lecturers_map_list)


    if 'department_id' in request.data:
        #get the department object
        department = Department.objects.get(id=request.data.get('department_id'))
        lecturers = lecturers.filter(department=department)
        pass


    class_courses = ClassCourse.objects.filter(lecturer__in=lecturers)


    if 'course_code' in request.data:
        course = Course.objects.get(course_code=request.data.get('course_code'))
        class_courses = class_courses.filter(course=course)
        pass

    if 'year' in request.data:
        class_courses = class_courses.filter(year=request.data.get('year'))
        pass

    if 'semester' in request.data:
        class_courses = class_courses.filter(semester=request.data.get('semester'))
        pass


    if not class_courses.exists():
        return Response([])


    lecturers_map_list = []

    for class_course in set(class_courses):
        lecturer = class_course.lecturer 
        #the lecturers class_courses
        lecturer_cc = class_courses.filter(lecturer=lecturer)
        
        lecturers_map_list.append(buildParamLecturerMap(lecturer, lecturer_cc))


    lecturers_map_list = sorted(
            lecturers_map_list, 
            key=lambda rating_map: rating_map['parameter_rating'], reverse=True)


    return Response(lecturers_map_list)








@api_view(['GET', 'POST'])
def getCourseRatings(request):
    request_data = request.data

    # Base queryset
    class_courses = ClassCourse.objects.all()

    # Filter by department
    if 'department_id' in request_data:
        department = Department.objects.get(id=request_data['department_id'])

        #ge all the lecturers in the specified department
        lecturers = Lecturer.objects.filter(department=department)

        #get all the class_courses handled by these lecturers
        class_courses = class_courses.filter(lecturer__in=lecturers)


    # Filter by year
    if 'year' in request_data:
        class_courses = class_courses.filter(year=request_data['year'])


    # Filter by semester
    if 'semester' in request_data:
        class_courses = class_courses.filter(semester=request_data['semester'])


    # Build the set of courses
    courses = set(cc.course for cc in class_courses)

    # Map courses to ratings
    courses_ratings_map = [
        buildCourseRateMap(course, class_courses.filter(course=course))
        for course in courses
    ]

    # Sort by parameter rating
    courses_ratings_map = sorted(
        courses_ratings_map,
        key=lambda crm: crm['parameter_mean_score'],
        reverse=True
    )

    return Response(courses_ratings_map)





@api_view(['GET'])
@requires_roles(['superuser', 'admin'])
def getDashboardGraphData(request):

    from selc_core.core_utils import create_classes_chart_info

    class_courses = ClassCourse.getCurrentClassCourses()

    dashboard_graph_data = create_classes_chart_info(class_courses)
    return Response(dashboard_data)


