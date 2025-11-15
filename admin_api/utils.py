

from django.contrib.auth.models import User, Group
from selc_core.models import Questionnaire, ClassCourse, Evaluation, Lecturer, StudentClass
from selc_core.models import Course
from selc_core.models import LecturerRating

from rest_framework.response import Response

ANSWER_SCORE_DICT = {

    #for performance
    'excellent': 5,
    'very good': 4,
    'good': 3,
    'average': 2,
    'bad': 1,
    'poor': 1,

    #for time
    'always': 5,
    'very often': 4,
    'sometimes': 3,
    'rarely': 2,
    'bever': 1,

    #for yes no questions
    'yes': 5,
    'no': 1,


    #for when the user gave No answer
    'no answer': 0
}




def categoryScoreBasedRemark(score: float):

    if score >= 0 and score <= 1.99:
        return 'Poor'

    elif score >= 2 and score <= 2.99:
        return 'Average'

    elif score >= 3 and score <= 3.5:
        return 'Good'

    elif score >= 3.6 and score <= 4.5:
        return 'Very Good'

    elif score >= 4.6 and score <= 5:
        return 'Excellent'

    return "Remark not found"




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
    user_map = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_superuser': user.is_superuser,
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
        total_cc_mean_score += cc.computeGrandMeanScore()

        pass


    parameter_mean_core = 0
    percentage_score = 0

    if len(class_courses) > 0:
        parameter_mean_score = total_cc_mean_score / number_of_lecturers
        percentage_score = (parameter_mean_score / 5) * 100

    course_rate_map['parameter_mean_score'] = parameter_mean_score
    course_rate_map['percentage_score'] = percentage_score
    course_rate_map['remark'] = categoryScoreBasedRemark(parameter_mean_score)
    course_rate_map['number_of_lecturers'] = number_of_lecturers
    course_rate_map['number_of_students'] = number_of_students
    course_rate_map['number_of_evaluated_students'] = number_of_evaluated_students

    return course_rate_map




def groupQuestionAnswerSummary(class_courses) -> dict:

    questions = Questionnaire.objects.all()

    """
        {
            question_number: {
                'answer_type':  answer_type,
                'question': actual question
                'answer_summary': {
                    'answer_variation_one': 1, 
                    'answer_variation_two': 2 
                }
            },

        }
    """

    eval_answer_map: dict[int, dict[str, int]] = {}

    for question in questions:

        question_id = question.q_id

        if question_id not in eval_answer_map:
            eval_answer_map[question_id] = {
                'answer_type': question.answer_type,
                'question': question.question,
                'answer_summary': {}  # creates and empty dictionary for keeping summary of the answers variations to a question
            }  # building another dictionary
            pass
            
            
    
        for class_course in class_courses:
            
            # filter the evaluation based on the class course.
            evaluations = Evaluation.objects.filter(class_course=class_course, question=question) 

            for evaluation in evaluations:
                answer = evaluation.answer

                answerNotInSummary = answer not in eval_answer_map[question_id]['answer_summary']
                
                if answerNotInSummary:
                    eval_answer_map[question_id]['answer_summary'][answer] = Evaluation.objects.filter(class_course=class_course, question_id=question, answer=answer).count()
                    continue

            pass
        pass


    return eval_answer_map





