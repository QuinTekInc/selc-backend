

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from selc_core.models import *
from rest_framework.status import *
from rest_framework.permissions import AllowAny

# Create your views here.

#all the data returned from this function is requested from the IT directorate's server.
#except that of the questionnaires.
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def loginStudent(request):

    #extract the student's information from the request data dictionary.
    username = request.data.get('username')
    password = request.data.get('password')



    user_filter = User.objects.filter(username=username)

    if not user_filter.exists():
        return Response({'message': 'Incorrect username or password'}, status=HTTP_401_UNAUTHORIZED)


    print('user filter length: ', len(user_filter))

    #search for a match in the Student's database.
    user = user_filter.first()

    if not user.check_password(password):
        return Response({'message': 'Incorrect username or password'}, status=HTTP_401_UNAUTHORIZED)
    

    if not user.groups.filter(name='student').exists():
        return Response({'message': 'You must be a student to be able to login'}, status=HTTP_403_FORBIDDEN)

    

    login(request, user)

    student = Student.objects.get(user=user)
    student_info_dict = student.toMap()


    return Response(student_info_dict)





@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def logoutStudent(request):
    user: User = request.user
    logout(request)

    return Response({'message': f'Student, {user.username}, logged out.'})




@api_view(['GET'])
def checkEnableEvaluations(request):
    return Response({'enable_evaluations': GeneralSetting.objects.all().first().enable_evaluations})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getRegisteredCourses(request):

    student = Student.objects.get(user=request.user)
    #search through the StudentClass table with student_info and the current_year and the current semester.
    student_classes = StudentClass.objects.filter(student=student)

    courses_list: list[dict] = [student_class.toMap() for student_class in student_classes]

    return Response(courses_list)





@api_view(['GET'])
def getQuestions(request):

    #question categories
    question_categories = QuestionCategory.objects.all()

    #group the questionnaires into their categories in a dictionary.
    categories_dict_list: list[dict] = []

    for category in question_categories:

        #a list to store the questions in the of dictionary
        questions_dict_list = [question.toMap() for question in category.getQuestions()]

        category_dict = {
            'category': category.cat_name,
            'questions': questions_dict_list
        }

        categories_dict_list.append(category_dict)

        pass

    
    return Response(categories_dict_list)





#for submitting the evaluation of a particular course together with its suggestion.
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def submitEvaluationData(request):
    
    request_data = request.data


    if not GeneralSetting.objects.all().first().enable_evaluations:
        return Response({'message': 'You evaluation reponse cannot be submitted. Evaluation submission has been disabled.'}, status=HTTP_403_FORBIDDEN)

    student = Student.objects.get(user=request.user)

    class_course = ClassCourse.objects.get(id=request_data['cc_id'])

    student_class = StudentClass.objects.get(student=student, class_course=class_course)


    # try:
    #     eval_suggestion = EvaluationSuggestion.objects.get(class_course=class_course, student=student)
    #     eval_suggestion.suggestion = request_data['suggestion']
    # except EvaluationSuggestion.DoesNotExist:
    #     eval_suggestion = EvaluationSuggestion.objects.create(class_course=class_course, student=student,
    #                                                           suggestion=request_data['suggestion'])


    eval_suggestion, _ = EvaluationSuggestion.objects.get_or_create(class_course=class_course, student=student,)
    eval_suggestion.suggestion = request_data['suggestion']

    lecturer_rating, _ = LecturerRating.objects.get_or_create(student=student, class_course=class_course,)
    lecturer_rating.rating = request_data['rating']

    # retrieve the answers from the server.
    answers_dict = request_data['answers']

    for answer_dict in answers_dict:

        question_id = answer_dict['question_id']
        answer = answer_dict['answer']

        question = Questionnaire.objects.get(q_id=question_id)

        # evaluation = Evaluation.objects.get(question_id=question, cc_id=classCourse, student_id=student)

        # try:
        #     evaluation = Evaluation.objects.get(student=student, question=question, class_course=class_course)
        #     evaluation.answer = answer
        # except Evaluation.DoesNotExist:
        #     evaluation = Evaluation.objects.create(student=student, question=question, class_course=class_course,
        #                                            answer=answer)
        

        evaluation, _ = Evaluation.objects.get_or_create(student=student, question=question, class_course=class_course)
        evaluation.answer = answer
        evaluation.save()
        pass

    lecturer_rating.save()
    eval_suggestion.save()


    student_class.evaluated = True
    student_class.save()

    return Response({'message': 'Your evaluation has been saved to the SELC server'})



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def getEvaluationForCourse(request, cc_id):

    student = Student.objects.get(user=request.user)

    class_course = ClassCourse(id=cc_id)

    evalAnswers = Evaluation.objects.filter(student=student, class_course=class_course)

    #form a questionnaire_category -> list_of_answers here.

    answer_cat_dict: dict[str: list] = {}

    for answer in evalAnswers:

        questionnaire = answer.question

        category = questionnaire.category.cat_name

        answer_dict = {
            'question': questionnaire.question,
            'answer': answer.answer
        }

        if category not in answer_cat_dict:
            answer_cat_dict[category] = [answer_dict]
        else:
            answer_cat_dict[category].append(answer_dict)

        pass
    
    #regroup the answers in the form [{'cat_name': questionnaire_category_name, 'answers': list of the answers to the questionnaires.}]
    answers_list_map = []

    for cat_key in answer_cat_dict.keys():

        cat_group_dict = {
            'cat_name': cat_key,
            'answers': answer_cat_dict[cat_key]
        }

        answers_list_map.append(cat_group_dict)

    eval_suggestion = EvaluationSuggestion.objects.get(student=student, class_course=class_course)
    suggestion = ''

    if eval_suggestion:
        suggestion = eval_suggestion.suggestion
        pass


    lecturer_rating: LecturerRating = LecturerRating.objects.get(student=student, class_course=class_course)
    

    response_dict = {
        'eval_answers': answers_list_map,
        'rating': lecturer_rating.rating,
        'suggestion': suggestion
    }


    return Response(response_dict)