


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
    'No': 0,
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


