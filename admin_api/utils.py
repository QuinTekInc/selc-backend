

from django.contrib.auth.models import User, Group
from selc_core.models import Questionnaire, ClassCourse, Evaluation, Lecturer, StudentClass
from selc_core.models import Course
from selc_core.models import LecturerRating

from rest_framework.response import Response

ANSWER_SCORE_DICT = {

    #for performance
    'Excellent': 5,
    'Very Good': 4,
    'Good': 3,
    'Average': 2,
    'bad': 1,

    #for time
    'Always': 5,
    'Very Often': 4,
    'Sometimes': 3,
    'Rarely': 2,
    'Never': 1,

    #for yes no questions
    'Yes': 5,
    'No': 1,


    #for when the user gave No answer
    'No Answer': 0
}




def categoryRemarkBasedScore(score: float):

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
        ratings_list = [lr.rating for lr in LecturerRating.objects.filter(class_course=cc)]
        total_rating += sum(ratings_list)
        number_of_students += len(ratings_list)


    if number_of_students == 0:
        return 0, 0


    average_rating = total_rating / number_of_students

    return number_of_students, average_rating



def buildParamLecturerMap(lecturer: Lecturer, class_courses) -> dict:

    lecturer_param_map: dict[str: object] = lecturer.toMap()

    lecturer_param_map['number_of_courses'] = len(class_courses)

    param_rating_student_count = parameterRatingAndStudentCount(lecturer, class_courses)

    lecturer_param_map['number_of_students'] = param_rating_student_count[0]
    lecturer_param_map['parameter_rating'] = param_rating_student_count[1]

    return lecturer_param_map




def buildCourseRateMap(course: Course, class_courses: list[ClassCourse]) -> dict:
    course_rate_map: dict[str: object] = course.toMap()


    total_sum = 0
    number_of_students = 0
    #total number of evaluations of questions with the answer type of performance
    number_of_performance = 0

    for cc in class_courses:

        student_classes = StudentClass.objects.filter(class_course=cc)
        number_of_students += len(student_classes)

        #get the evaluations of the class courses based on the questionnaires with performance answer types.
        evaluations = Evaluation.objects.filter(class_course=cc)

        #filter the evaluations to extract the questionnaires with the performance answer types.
        evaluations = list(filter(lambda _evaluation: _evaluation.question.answer_type == 'performance', evaluations))
        number_of_performance += len(evaluations)

        for evaluation in evaluations:
            total_sum += ANSWER_SCORE_DICT.get(evaluation.answer, 0)
            pass

        pass


    course_performance_score = 0

    if number_of_performance != 0:
        course_performance_score = total_sum / number_of_performance

    course_rate_map['parameter_rating'] = course_performance_score
    course_rate_map['number_of_students'] = number_of_students

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

    eval_answer_map: dict[int: dict[str: int]] = {}

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





