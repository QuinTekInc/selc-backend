#openpyxl libraries
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, Alignment

from selc_core.models import ClassCourse
from selc_core.report_generators import report_commons


class AdminExcelReport:

    def __init__(self):
        #get all the class_courses for the semester
        self.class_courses: list = ClassCourse.getCurrentClassCourses()

        self.work_book = report_commons.create_workbook()

        pass

    def questionnaire_answer_sheet(self):

        ws = self.work_book.create_sheet(title='Questionnaire Answer Summary')


        #set the column widths
        column_widths = {1: 20, 2: 50, 3: 10, 4: 10, 5: 15, 6: 10, 7: 15, 8: 15, 9: 15, 10: 20}
        report_commons.set_column_widths(ws, column_widths)

        report_commons.init_sheet_title(ws, title='Quality Assurance and Academic Planning Directorate')
        report_commons.init_sheet_title(ws, title='University of Energy And natural Resource', row=2)


        row: int = 4

        for class_course in self.class_courses:
            new_row = self.build_questionnaire_evaluation_cell(ws, class_course, row)
            row += new_row + 5
            pass


        pass

    def categories_score_sheet(self):
        pass

    def lecturer_rating_sheet(self):
        pass

    def response_rate_sheet(self):
        pass

    def suggestion_sentiments_summary_sheet(self):
        pass


    def build_questionnaire_evaluation_cell(self, sheet: Worksheet,  class_course: ClassCourse, q_start_row) -> int:

        cc_map = class_course.toMap()

        #create the detail cells

        """
        Name of Lecturer: name  ------- Semester: semester
        Course title: title ------ Course Code: code ---- credit_hours: credit_hours
        Number of Students in Class: number of students ----------  Number of respondents: credit ---- Response rate: response rate
        Department roll: number on roll ----- Lecturer rating for course: l_rating
        course_score: average score ---- percentage score: percentage ----- remark: generated remark
        
        """

        #name detail cells
        self.build_field_cell(sheet, row=q_start_row, column=1, value='Name of Lecturer')

        sheet.cell(row=q_start_row, column=2, value=class_course.lecturer.getFullName())  #spans 3 columns BCD
        #perform necessary row merging
        sheet.merge_cells(start_row=q_start_row, start_column=2, end_row=q_start_row, end_column=4)

        # semester detail cells
        self.build_field_cell(sheet, row=q_start_row, column=5, value='Semester')

        sheet.cell(row=q_start_row, column=6, value=class_course.semester)  #spans 5 columns FGHIJ
        sheet.merge_cells(start_row=q_start_row, start_column=6, end_row=q_start_row, end_column=10)

        #==================next row=========================================

        q_start_row += 1

        # course code cells
        self.build_field_cell(sheet, row=q_start_row, column=1, value='Course Code')

        sheet.cell(row=q_start_row, column=2, value=class_course.course.course_code) #spans 3 columns BCD
        sheet.merge_cells(start_row=q_start_row, start_column=2, end_row=q_start_row, end_column=4)

        # course title cells
        self.build_field_cell(sheet, row=q_start_row, column=5, value='Course Title')

        sheet.cell(row=q_start_row, column=6, value=class_course.course.title) #span 3 columns FGH
        sheet.merge_cells(start_row=q_start_row, start_column=6, end_row=q_start_row, end_column=8)

        # credit hour cells
        self.build_field_cell(sheet, row=q_start_row, column=9, value='Credit Hours')

        sheet.cell(row=q_start_row, column=10, value=class_course.credit_hours)


        #=================next row============================================

        q_start_row += 1

        # number on roll cells
        self.build_field_cell(sheet, row=q_start_row, column=1, value='Number of Students')

        sheet.cell(row=q_start_row, column=2, value=cc_map['number_of_registered_students']) #spans 3 columns BCD
        sheet.merge_cells(start_row=q_start_row, start_column=2, end_row=q_start_row, end_column=4)



        # respondent cells
        self.build_field_cell(sheet, row=q_start_row, column=5, value='Number of respondents')

        sheet.cell(row=q_start_row, column=6, value=cc_map['number_of_evaluated_students'])
        sheet.merge_cells(start_row=q_start_row, start_column=6, end_row=q_start_row, end_column=8)

        # response rate cells
        self.build_field_cell(sheet, row=q_start_row, column=9, value='Response Rate')

        sheet.cell(row=q_start_row, column=10, value=cc_map['response_rate'])


        # ==================next row=========================================

        q_start_row += 1

        # department cells
        self.build_field_cell(sheet, row=q_start_row + 3, column=1, value='Department')

        sheet.cell(row=q_start_row + 3, column=2, value=class_course.lecturer.department.department_name)  #spans 3 columns BCD
        sheet.merge_cells(start_row=q_start_row, start_column=2, end_row=q_start_row, end_column=4)

        # Lecturer rating for course cells
        self.build_field_cell(sheet, row=q_start_row, column=5, value='Lecturer rating for this course')

        sheet.cell(row=q_start_row, column=6, value=cc_map['lecturer_course_rating'])  #spans 5 columns FGHIJ
        sheet.merge_cells(start_row=q_start_row, start_column=6, end_row=q_start_row, end_column=10)

        # ==================next row=========================================

        q_start_row += 1

        # Course score cell
        self.build_field_cell(sheet, row=q_start_row, column=1, value='Mean Score')

        sheet.cell(row=q_start_row, column=2, value=cc_map['grand_mean_score']) #spans 3 columns BCD
        sheet.merge_cells(start_row=q_start_row, start_column=2, end_row=q_start_row, end_column=4)

        # percentage course score cells
        self.build_field_cell(sheet, row=q_start_row, column=5, value='Percentage Score')

        sheet.cell(row=q_start_row , column=6, value=cc_map['grand_percentage']) #spans 3 columns FGH
        sheet.merge_cells(start_row=q_start_row, start_column=6, end_row=q_start_row, end_column=8)

        # remarks
        self.build_field_cell(sheet, row=q_start_row, column=9, value='Remark')

        sheet.cell(row=q_start_row, column=10, value=cc_map['remark'])



        #todo: populating the headers [header title, span]
        headers = [
            'Core Area (Categories)',
            'Question',
            'Q Mean Score',
            'Q Percentage Score',
            'C Mean Score',
            'C Percentage Score',
            'C Remark',
            'Grand Mean Score',
            'Percentage Score',
            'Remark'
        ]

        report_commons.init_header_cells(sheet, headers, row=q_start_row + 5)


        #for populating the actual categories and questions data
        q_start_row += 1
        row = q_start_row


        #get the evaluation
        evaluation_summary = class_course.getEvalDetails()


        #loop for categories
        for eval_item in evaluation_summary:

            #get the category
            category = eval_item['category']
            cat_mean_score = eval_item['mean_score']
            cat_percentage_score = eval_item['percentage_score']
            cat_remark = eval_item['remark']

            questions = eval_item['questions']


            sheet.cell(row=row, column=1, value=category)

            start_row = row
            end_row = start_row + len(questions) -1

            #inner loop for populating the questions
            for question_item in questions:
                question = question_item['question']
                q_mean_score = question_item['mean_score']
                q_percentage_score = question_item['percentage_score']

                sheet.cell(row=row, column=2, value=question)
                sheet.cell(row=row, column=3, value=q_mean_score)
                sheet.cell(row=row, column=4, value=q_percentage_score)

                row += 1
                pass

            sheet.cell(row=start_row, column=5, value=cat_mean_score)
            sheet.cell(row=start_row, column=6, value=cat_percentage_score)
            sheet.cell(row=start_row, column=7, value=cat_remark)


            #todo: merge necessary cells
            #category cell
            sheet.merge_cells(start_row=start_row, start_column=1, end_row=end_row, end_column=1)
            # mean score cell
            sheet.merge_cells(start_row=start_row, start_column=5, end_row=end_row, end_column=5)
            # percentage score cell
            sheet.merge_cells(start_row=start_row, start_column=6, end_row=end_row, end_column=6)
            # category remark cell
            sheet.merge_cells(start_row=start_row, start_column=7, end_row=end_row, end_column=7)

            pass


        #grand mean score
        sheet.cell(row=q_start_row, column=8, value=cc_map['grand_mean_score'])
        sheet.merge_cells(start_row=q_start_row, start_column=8, end_row=row, end_column=8)

        #grand percentage score
        sheet.cell(row=q_start_row, column=9, value=cc_map['grand_percentage'])
        sheet.merge_cells(start_row=q_start_row, start_column=9, end_row=row, end_column=9)

        #final remark
        sheet.cell(row=q_start_row, column=10, value=cc_map['remark'])
        sheet.merge_cells(start_row=q_start_row, start_column=10, end_row=row, end_column=10)

        return row



    def build_field_cell(self, sheet: Worksheet,  row: int, column: int, value):
        field_cell = sheet.cell(row=row, column=column, value=value)
        field_cell.font = Font(bold=True, size=11)
        field_cell.alignment = Alignment(vertical='center', horizontal='left', wrapText=True, )

        return field_cell

    pass
