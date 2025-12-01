from django.shortcuts import render
from django.http import HttpResponse

from admin_api.decorators import requires_roles
from .models import Department, ClassCourse, ReportFile, GeneralSetting

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import *


from .report_generators import course_eval_report, admin_report, departmental_report

# Create your views here.


"""
{
    'report_type': 'admin' or 'department' or 'class_course',
    'id': cc_id or department_id   note that admin reports do not require id's.
    'semester': academic_semester
    'year': academic_year
}
"""

@api_view(['GET', 'POST'])
def generate_report(request):

    request_data = request.data

    
    report_type = request_data.get("report_type", None)
    is_regenerate = request_data.get('regenerate', False) # should the report be regenerated?

    if report_type not in ['class_course', 'department', 'admin']:
        return Response({'message': 'Specify report type'}, status=HTTP_400_BAD_REQUEST)


    general_setting = GeneralSetting.objects.first()

    academic_year = request_data.get('year', general_setting.academic_year)
    semester = request_data.get('semester', general_setting.current_semester)


    ys_prefix = f'{academic_year}0{semester}'  # prefix for the date and time.

    file_name = ''


    class_course = None
    department = None

    #check it is a class_course
    if report_type == 'class_course':
        class_course = ClassCourse.objects.get(id=request_data['id'])
        file_name = class_course.getSavableReportFileName()
        pass

    elif report_type == 'department':
        department = Department.objects.get(id=request_data['id'])
        file_name = f'{ys_prefix}_{department.getSavableReportFileName()}'
        pass

    elif report_type == 'admin':
        file_name = f'{ys_prefix}_admin_report'
        pass



    reportfile_objects = ReportFile.objects.filter(file_name=file_name)

    if reportfile_objects.exists() and not is_regenerate:
        report_file_url = reportfile_objects.first().file.path
        return Response(report_file_url)


    report = None

    if report_type == 'admin':
        report = admin_report.AdminExcelReport(year=academic_year, semester=semester)

    elif report_type == 'class_course':
        report = course_eval_report.CourseEvalExcelReport(class_course)

    elif report_type == 'department':
        report = departmental_report.DepartmentalExcelReport(department=department)

    report.save()

    reportfile_object = ReportFile.objects.get(file_name=file_name)

    return Response({'file_url': reportfile_object.file.path})



@api_view(['GET'])
@requires_roles(['admin'])
def get_all_files(request, cc_id: int):

    report_files = ReportFile.objects.all()

    return Response([report_file.toMap() for report_file in report_files])

