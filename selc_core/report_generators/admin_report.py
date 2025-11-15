#openpyxl libraries


from selc_core.models import ClassCourse


class AdminExcelReport:

    def __init__(self):
        #get all the class_courses for the semester
        class_courses = ClassCourse.getCurrentClassCourses()

    def questionnaire_answer_sheet(self):
        pass

    def categories_score_sheet(self):
        pass

    def lecturer_rating_sheet(self):
        pass

    def response_rate_sheet(self):
        pass

    def suggestion_sentiments_summary_sheet(self):
        pass

        pass
