
from .models import LecturerRating, EvaluationSuggestion

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

    lrating_map = {}

    for rating in range(5, -1, -1):
        lrating_map[rating] = lecturer_ratings.filter(rating=rating).count()
        pass


    #TODO: FINDING THE OVERALL SUGGESTION SENTIMENTS FOR THE GIVEN SET OF CLASS COURSES
    suggestions = EvaluationSuggestion.objects.filter(class_course__in=class_courses)

    sentiments_map = {}

    for sentiment in ['negative', 'neutral', 'positive']:
        sentiments_map[sentiment] = suggestions.filter(sentiment=sentiment).count()
        pass


    chart_data = {
        'registration_summary': reg_map,
        'lecturer_rating': lrating_map,
        'sentiment_summary': sentiments_map
    }


    return chart_data


