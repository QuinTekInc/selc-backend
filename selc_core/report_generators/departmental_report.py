from openpyxl.workbook import Workbook
from openpyxl.worksheet import worksheet

from selc_core.models import Department, Lecturer, ClassCourse


class DepartmentalExcelReport:

    def __init__(self, department: Department) -> None:
        self.department = department

        #get the lectures in the department
        self.lecturers = Lecturer.objects.filter(department=department)
        #get the class_courses offered by lectures in the department
        self.class_courses = ClassCourse.getCurrentClassCourses().filter(lecturer__in=self.lecturers)

        #create a work book here.
        self.work_book = Workbook()

        pass

    def overview_sheet(self):
        pass

    def questionnaire_answer_summary_sheet(self):
        pass

    def category_scores_sheet(self):
        pass

    def response_rate_sheet(self):
        pass

    def lecturer_rating_summary_sheet(self):
        pass

    def suggestion_sentiments_summary_sheet(self):
        pass

    pass
