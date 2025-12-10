from openpyxl.styles import Alignment, Font
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter

from selc_core.core_utils import getScoreRemark
from selc_core.models import ClassCourse, Course
from selc_core.models import ReportFile

from . import report_commons

from django.core.files.base import File


class CourseEvalExcelReport:

    def __init__(self, class_course: ClassCourse):

        self.class_course = class_course

        self.lecturer = class_course.lecturer

        self.work_book = Workbook()

        #remove the default work sheet.
        self.work_book.remove(self.work_book.active)


        #load the category info
        self.eval_summary = self.class_course.getEvalDetails()


        self.overview_sheet()
        self.questionnaire_answer_summary_sheet()
        self.category_scores_sheet()
        self.lecturer_rating_summary_sheet()
        self.suggestion_sentiments_summary_sheet()

        self.save()

        pass





    def overview_sheet(self):
        ws = self.work_book.create_sheet(title='Overview')

        number_of_students, evaluated_students = self.class_course.getNumberOfRegisteredStudents()
        response_rate = (evaluated_students / number_of_students) * 100


        course_mean_score, percentage_score = self.class_course.computeGrandMeanScore()

        # lecturer name
        # department
        # course code
        # course title
        # credit hours
        # semester
        # academic year
        # number of registered students
        # evaluated students
        # response rate
        # course score
        # percentage score
        # average sentiment
        # lecturer rating for this course.

        overview_list = [
            ('Lecturer Name', self.class_course.lecturer.getFullName()),
            ('Department', self.class_course.lecturer.department.department_name),
            ('Course code', self.class_course.course.course_code),
            ('Course title', self.class_course.course.title),
            ('Credit Hours', self.class_course.credit_hours),
            ('Semester', self.class_course.semester),
            ('Academic year', self.class_course.year),
            ('Number of Students', number_of_students),
            ('Evaluated Students', evaluated_students),
            ('Response Rate', response_rate),
            ('Mean Score', course_mean_score),
            ('Percentage Score', percentage_score),
            ('Remark', getScoreRemark(course_mean_score)),
            ('Lecturer Rating for this course', self.class_course.computeLecturerRatingForCourse())
        ]


        report_commons.init_sheet_title(ws, title='Course Evaluation Overview', span_column=2)

        report_commons.set_column_widths(ws, {1: 30, 2: 50})



        for row, overview_field in enumerate(overview_list, start=2):

            field_cell = ws.cell(row=row, column=1, value=overview_field[0])
            field_cell.alignment = Alignment(horizontal='center', vertical='center')
            field_cell.font = Font(bold=True)

            #data cell
            ws.cell(row=row, column=2, value=overview_field[1])
            pass

        pass



    def questionnaire_answer_summary_sheet(self):

        ws = self.work_book.create_sheet(title='Questionnaire Answers')

        headers = ['Question', 'Answer Type', 'Answer Option', 'Count', 'Average Score', 'Percentage Score', 'Remark']

        report_commons.init_sheet_title(ws, title='Questionnaire Answer Summary', span_column=len(headers))

        #create the headers.
        report_commons.init_header_cells(ws, headers=headers)
        report_commons.set_row_height(ws, 2, 0.4, in_inches=True)

        report_commons.set_column_widths(ws, {1: 50, 2: 10, 3: 10, 4: 12, 5: 15, 6: 15, 7: 10})

        # extract the questionnaire answer summaries
        questions_answer_summary: list = [question_dict for summary in self.eval_summary for question_dict in
                                          summary.get('questions', [])]
        '''
            {
              'question': 'Coverage of course content by lecturer',
              'answer_type': 'performance',
              'answer_summary': {
                'Poor': 0,
                'Average': 0,
                'Good': 0,
                'Very Good': 1,
                'Excellent': 0,
              },
              'percentage_score': 80.0,
              'average_score': 4.0,
              'remark': 'Very Good'
            },
            {
              'question': 'Communication of objectives of the course',
              'answer_type': 'performance',
              'answer_summary': {
                'Poor': 0,
                'Average': 0,
                'Good': 0,
                'Very Good': 1,
                'Excellent': 0,
              },
              'percentage_score': 80.0,
              'average_score': 4.0,
              'remark': 'Very Good'
            }
        '''


        row = 3

        for eval_summary_item in questions_answer_summary:

            question: str = eval_summary_item['question']
            answer_type: str = eval_summary_item['answer_type']
            answer_summary: dict = eval_summary_item['answer_summary']
            average_score: float = eval_summary_item['mean_score']
            percentage_score: float = eval_summary_item['percentage_score']
            remark: float = eval_summary_item['remark']


            #populate the question cell.
            report_commons.create_cell(ws, row=row, column=1, value=question)

            ws.cell(row=row, column=2, value=answer_type)

            start_row = row
            end_row = row + len(answer_summary) - 1

            for answer_entry in answer_summary.items():
                option, count = answer_entry

                ws.cell(row=row, column=3, value=option)
                ws.cell(row=row, column=4, value=count)

                row += 1
                pass

            ws.cell(row=start_row, column=5, value=average_score)

            ws.cell(row=start_row, column=6, value=percentage_score)

            ws.cell(row=start_row, column=7, value=remark)


            #todo: span the various cells apart to at the par with the cells of its corresponding answer_option and count cells.

            #spanning the question cell
            ws.merge_cells(start_row=start_row, start_column=1, end_row=end_row, end_column=1)

            # spanning the answer_type cell
            ws.merge_cells(start_row=start_row, start_column=2, end_row=end_row, end_column=2)

            # spanning the average score cell
            ws.merge_cells(start_row=start_row, start_column=5, end_row=end_row, end_column=5)

            # spanning the percentage score cell
            ws.merge_cells(start_row=start_row, start_column=6, end_row=end_row, end_column=6)

            # spanning the remark cell.
            ws.merge_cells(start_row=start_row, start_column=7, end_row=end_row, end_column=7)
            pass


        pass



    def category_scores_sheet(self):

        ws = self.work_book.create_sheet(title='Category Summary')

        headers = ['Core Area (Category)', 'Questions', 'Average Score', 'Percentage Score', 'Remark']

        report_commons.init_sheet_title(ws, title='Thematic Areas of Evaluation (Categories)', span_column=len(headers))

        report_commons.init_header_cells(ws, headers)
        report_commons.set_row_height(ws, 2, 0.4, in_inches=True)

        report_commons.set_column_widths(ws, {1: 30, 2: 50, 3: 15, 4: 15, 5: 10})


        category_summary: list = self.class_course.getEvalQuestionCategoryRemarks(include_questions=True)

        row = 3

        #todo: populate the categories scores here.
        for summary_item in category_summary:
            category: str = summary_item['category']
            questions: list = [question['question'] for question in summary_item['questions']]
            average_score: float = summary_item['average_score']
            percentage_score: float = summary_item['percentage_score']
            remark: str = summary_item['remark']

            ws.cell(row=row, column=1, value=category)

            start_row = row
            end_row = row + len(questions) - 1

            for question in questions:
                report_commons.create_cell(ws, row=row, column=2, value=question)
                row += 1
                pass

            ws.cell(row=start_row, column=3, value=average_score)
            ws.cell(row=start_row, column=4, value=percentage_score)
            ws.cell(row=start_row, column=5, value=remark)

            #todo: span the cells vertically
            #category cell
            ws.merge_cells(start_row=start_row, start_column=1, end_row=end_row, end_column=1)
            #average score cell
            ws.merge_cells(start_row=start_row, start_column=3, end_row=end_row, end_column=3)
            #percentage score cell
            ws.merge_cells(start_row=start_row, start_column=4, end_row=end_row, end_column=4)
            #remark
            ws.merge_cells(start_row=start_row, start_column=5, end_row=end_row, end_column=5)
            pass

        pass


    def lecturer_rating_summary_sheet(self):

        ws = self.work_book.create_sheet(title='Lecturer Rating')

        headers = ['Rating', 'Count', 'Percentage']

        report_commons.init_sheet_title(ws, title='Lecturer Rating Summary', span_column=len(headers))

        report_commons.init_header_cells(ws, headers)
        report_commons.set_row_height(ws, 2, 0.3, in_inches=True)

        report_commons.set_column_widths(ws, {1: 10, 2: 15, 3: 17})


        lecturer_rating_summary = self.class_course.getLecturerRatingDetails()


        row = 3

        for rating_summary in lecturer_rating_summary:
            rating = rating_summary['rating']
            count = rating_summary['rating_count']
            percentage = rating_summary['percentage']

            ws.cell(row=row, column=1, value=rating)

            ws.cell(row=row, column=2, value=count)

            ws.cell(row=row, column=3, value=percentage)

            row += 1
            pass

        pass




    def suggestion_sentiments_summary_sheet(self):

        ws = self.work_book.create_sheet(title='Sentiment Summary')

        headers = ['Sentiment', 'Count', 'Percentage']

        report_commons.init_sheet_title(ws, title='Suggestions Sentiment Summary', span_column=len(headers))

        report_commons.init_header_cells(ws, headers)
        report_commons.set_row_height(ws, 2, 0.3, in_inches=True)

        report_commons.set_column_widths(ws, {1: 20, 2: 15, 3: 17})

        sentiment_summary: list = self.class_course.getEvalSuggestions(include_suggestions=False)['sentiment_summary']

        row = 3

        for sentiment_summary_item in sentiment_summary:
            sentiment: str = sentiment_summary_item['sentiment']
            count: int = sentiment_summary_item['sentiment_count']
            percentage: float = sentiment_summary_item['sentiment_percent']

            ws.cell(row=row, column=1, value=sentiment)
            ws.cell(row=row, column=2, value=count)
            ws.cell(row=row, column=3, value=percentage)

            row += 1
            pass


        pass


    def save(self):
        file_name = self.class_course.getSavableReportFileName()
        file_type = '.xlsx'


        report_commons.saveWorkbook(self.work_book, file_name, file_type)
        pass


    pass

