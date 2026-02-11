
from .models import LecturerRating, EvaluationSuggestion

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ClassCourse, Lecturer

ANSWER_TYPE_DICT: dict ={
    "performance": ['Excellent', 'Very Good', 'Good', 'Average', 'Bad'],
    "time": ['Always', 'Very Often', 'Sometimes', 'Rarely', 'Never'],
    "yes_no": ['Yes', 'No']

}


ANSWER_SCORE_DICT = {
    #for performance
    'excellent': 5,
    'very good': 4,
    'good': 3,
    'average': 2,
    'bad': 1,

    #for time
    'always': 5,
    'very often': 4,
    'sometimes': 3,
    'often': 3,
    'rarely': 2,
    'never': 1,

    #for yes no questions
    'yes': 5,
    'no': 0,

    #for when the user gave No answer
    'no answer': 0
}





#remarks based on a score
#mostly used to get remarks for the category average score after class_course evaluation.
def getScoreRemark(score: float):

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







#normally used when deleting a questionnaire category from the database.
def replaceCategoryForQuestions(old_category, replacement_category):

    from .models import Questionnaire  #to prevent circular import.
    
    #get the qiestions with the old category
    questions = Questionnaire.objects.filter(category=old_category)

    if not questions:
        return

    #for each question, replace the old category with the new category
    for question in questions:
        question.category = replacement_category
        question.save()

    pass




#returns course rating, suggestion sentiments and response rates
#for a given set of ClassCourses
def create_classes_chart_info(class_courses) -> dict:

    #TODO: CALCULATING THE OVERALL RESPONSE RATE FOR THE GIVEN SET OF CLASS COURSES
    
    total_registrations_tup = [cc.getNumberOfRegisteredStudents() for cc in class_courses]

    total_registrations = sum([std_tup[0] for std_tup in total_registrations_tup]) 
    evaluated_registrations = sum([std_tup[1] for std_tup in total_registrations_tup])

    response_rate = (evaluated_registrations / total_registrations) if total_registrations != 0 else 0

    reg_map = {
        'total_registrations': total_registrations,
        'evaluated_registrations': evaluated_registrations,
        'response_rate': response_rate
    }

    #TODO: CALCULATING THE AVERAGE LECTURER RATINGS OBTAINED THE GIVEN SET OF CLASS COURSES
    lecturer_ratings = LecturerRating.objects.filter(class_course__in=class_courses)
    total_ratings = lecturer_ratings.count()

    lrating_map = {}

    for rating in range(5, 0, -1):

        rating_count = lecturer_ratings.filter(rating=rating).count()
        rating_percentage = (rating_count / total_ratings) * 100 if total_ratings != 0 else 0

        lrating_map[str(rating)] = lecturer_ratings.filter(rating=rating).count()
        lrating_map[f'rating_{rating}_percentage'] = rating_percentage

        pass


    #TODO: FINDING THE OVERALL SUGGESTION SENTIMENTS FOR THE GIVEN SET OF CLASS COURSES
    suggestions = EvaluationSuggestion.objects.filter(class_course__in=class_courses)
    total_suggestions = suggestions.count()

    sentiments_map = {}

    for sentiment in ['negative', 'neutral', 'positive']:
        sentiment_count = suggestions.filter(sentiment=sentiment).count()
        sentiment_percentage = (sentiment_count/total_suggestions) * 100 if total_suggestions != 0 else 0
        sentiments_map[sentiment] = suggestions.filter(sentiment=sentiment).count()
        sentiments_map[f'{sentiment}_percentage'] = sentiment_percentage
        pass


    '''
        response format:
        {
            'registration_summary':{
                'total_registrations': int,
                'evaluated_registrations': int,
                'response_rate': float
            },

            'lecturer_rating': {
                'total_students'
                5: int,
                4: int,
                3: int,
                2: int,
                1: int,
                0: int
            },

            'sentiment_summary':{
                'negative': int,
                'neutral': int,
                'positive': int
            }
        }
    '''


    chart_data = {
        'registration_summary': reg_map,
        'lecturer_rating': lrating_map,
        'sentiment_summary': sentiments_map
    }


    return chart_data




def trigger_admin_dashboard_update():

    class_courses = ClassCourse.getCurrentClassCourses()

    dashboard_data = create_classes_chart_info(class_courses)

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        'admin_dashboard', #channels group name
        {
            "type": 'admin_dashboard_event',
            'data': dashboard_data
        }
    )

    pass



def trigger_lecturer_dashboard_update(lecturer: Lecturer):

    class_courses = ClassCourse.objects.filter(lecturer=lecturer)
    dashboard_data = create_classes_chart_info(class_courses)

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f'lecturer_dashboard_{lecturer.user.username}', #channels group name
        {
            "type": 'lecturer_dashboard_event',
            'data': dashboard_data
        }
    )

    pass
