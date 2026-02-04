

from django.contrib.auth.models import User, Group
from selc_core.models import Questionnaire, ClassCourse, Evaluation, Lecturer, StudentClass
from selc_core.models import Course
from selc_core.models import LecturerRating

from rest_framework.response import Response
import selc_core.core_utils

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




def createSuperUser(username, password, email, first_name='', last_name=''):

    user = User.objects.create_superuser(
        username=username, password=password, 
        email=email, first_name=first_name,
        last_name=last_name
    )

    group = Group.objects.get(name='superuser')

    if group:
        user.groups.add(group)

    user.save()
    pass



#rename this function to 'buildUserAccountDict'
def createUserAccountDict(user: User, auth_token = None):

    group = user.groups.first()

    role = group.name if group is not None else None

    if role is None and user.is_superuser:
        role = 'superuser'

    user_map = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': role,
        'is_active': user.is_active
    }

    if auth_token:
        user_map['auth_token'] = auth_token.key


    return user_map





def calculateLecturerRating(lecturer: Lecturer) -> float:

    #here we have to get all the courses taught the lecturer.
    class_courses = ClassCourse.objects.filter(lecturer_id=lecturer)

    number_of_ratings = 0
    ratings_sum = 0

    for cc in class_courses:
        lecturer_ratings = LecturerRating.objects.filter(class_course=cc)

        number_of_ratings += len(lecturer_ratings)

        for lr in lecturer_ratings:
            ratings_sum += lr.rating
            pass

        pass


    if number_of_ratings == 0:
        return 0


    average_rating = ratings_sum / number_of_ratings

    return average_rating




def parameterRatingAndStudentCount(lecturer: Lecturer, class_courses: list[ClassCourse]) -> tuple:

    number_of_students = 0
    total_rating = 0

    for cc in class_courses:
        #get the ratings list from the evaluated class courses according to the parameters provided.
        course_lecturer_ratings = LecturerRating.objects.filter(class_course=cc)
        ratings_list = [lr.rating for lr in LecturerRating.objects.filter(class_course=cc)]
        total_rating += sum(ratings_list)
        number_of_students += len(ratings_list)


    if number_of_students == 0:
        return 0, 0


    average_rating = total_rating / number_of_students

    return number_of_students, average_rating



#todo: rename this function to 'buildParamLecturerRatingMap'
def buildParamLecturerMap(lecturer: Lecturer, class_courses) -> dict:

    lecturer_param_map: dict[str: object] = lecturer.toMap()

    #number of coures taught by the lecturer
    lecturer_param_map['number_of_courses'] = len(class_courses) 

    param_rating_student_count = parameterRatingAndStudentCount(lecturer, class_courses)

    lecturer_param_map['number_of_students'] = param_rating_student_count[0] #this time its the number of students who rated this lecturer.
    lecturer_param_map['parameter_rating'] = param_rating_student_count[1]

    return lecturer_param_map




#todo: rename this function to 'buildParamCourseScoreMap'
def buildCourseRateMap(course: Course, class_courses: list[ClassCourse]) -> dict:

    course_rate_map: dict[str, object] = course.toMap()

    number_of_lecturers = len(class_courses) #because each class_course has a lecturer (automatically :->)

    total_cc_mean_score = 0
    number_of_students = 0
    number_of_evaluated_students = 0

    for cc in class_courses:


        registered_students_count_data = cc.getNumberOfRegisteredStudents()

        #get the number of students
        number_of_students += registered_students_count_data[0]
        number_of_evaluated_students += registered_students_count_data[1]

        #add the mean score for this current class course to the total_cc_mean_score
        total_cc_mean_score += cc.computeGrandMeanScore()[0]

        pass


    parameter_mean_score = 0
    percentage_score = 0

    if len(class_courses) > 0:
        parameter_mean_score = total_cc_mean_score / number_of_lecturers
        percentage_score = (parameter_mean_score / 5) * 100

    course_rate_map['parameter_mean_score'] = parameter_mean_score
    course_rate_map['percentage_score'] = percentage_score
    course_rate_map['remark'] = selc_core.core_utils.getScoreRemark(parameter_mean_score)
    course_rate_map['number_of_lecturers'] = number_of_lecturers
    course_rate_map['number_of_students'] = number_of_students
    course_rate_map['number_of_evaluated_students'] = number_of_evaluated_students

    return course_rate_map



