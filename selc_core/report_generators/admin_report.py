#openpyxl libraries
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, Alignment

from . import report_commons
from .bulk_report import BulkExcelReport

from selc_core.models import ClassCourse, QuestionCategory, GeneralSetting



class AdminExcelReport:

    def __init__(self, year=None, semester=None):
        #get all the class_courses for the semester


        general_setting = GeneralSetting.objects.first()

        self.year = year if year is not None else general_setting.academic_year

        self.semester = semester if semester is not None else general_setting.current_semester

        if year is None and semester is None:
            self.class_courses = ClassCourse.getCurrentClassCourses()
        else:
            self.class_courses = ClassCourse.objects.filter(year=self.year, semester=self.semester)
            pass


        self.work_book: Workbook = report_commons.create_workbook()

        self.bulk_report = BulkExcelReport(self.work_book, self.class_courses)

        pass



    def save(self):
        general_setting = GeneralSetting.objects.first()
        file_name = f'{self.year}0{self.semester}_admin_report'
        file_type = '.xlsx'

        report_commons.saveWorkbook(self.work_book, file_name=file_name, file_type=file_type)

    pass
