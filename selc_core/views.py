from django.shortcuts import render
from django.http import HttpResponse, FileResponse

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

# @api_view(['POST'])
# def generate_report(request):

#     request_data = request.data

    
#     report_type = request_data.get("report_type", None)
#     is_regenerate = request_data.get('regenerate', False) # should the report be regenerated?
#     file_type = request_data.get('file_type', '.xlsx')
    

#     if report_type not in ['class_course', 'department', 'admin']:
#         return Response({'message': 'Specify report type'}, status=HTTP_400_BAD_REQUEST)


#     general_setting = GeneralSetting.objects.first()

#     academic_year = request_data.get('year', general_setting.academic_year)
#     semester = request_data.get('semester', general_setting.current_semester)


#     ys_prefix = f'{academic_year}0{semester}'  # prefix for the year and semester

#     file_name = ''


#     class_course = None
#     department = None

#     #check it is a class_course
#     if report_type == 'class_course':
#         class_course = ClassCourse.objects.get(id=request_data['id'])
#         file_name = class_course.getSavableReportFileName()
#         pass

#     elif report_type == 'department':
#         department = Department.objects.get(id=request_data['id'])
#         file_name = f'{ys_prefix}_{department.getSavableReportFileName()}'
#         pass

#     elif report_type == 'admin':
#         file_name = f'{ys_prefix}_admin_report'
#         pass



#     reportfile_objects = ReportFile.objects.filter(file_name=file_name, file_type=file_type)

#     if reportfile_objects.exists() and not is_regenerate:
        
#         report_file_url = reportfile_objects.first().file.path

#         return FileResponse(
#             reportfile_object.file, 
#             as_attachment=True, 
#             filename=f'{file_name}.{reportfile_object.file_type}'
#         )


#     report = None

#     if report_type == 'admin':
#         report = admin_report.AdminExcelReport(year=academic_year, semester=semester)

#     elif report_type == 'class_course':
#         report = course_eval_report.CourseEvalExcelReport(class_course)

#     elif report_type == 'department':
#         report = departmental_report.DepartmentalExcelReport(department=department)

#     report.save() #each report class has the 'save' method

#     reportfile_object = ReportFile.objects.get(file_name=file_name)

#     return FileResponse(
#         reportfile_object.file, 
#         as_attachment=True, 
#         filename=f'{file_name}.{reportfile_object.file_type}'
#     )





@api_view(['POST'])
def generate_report(request):

    request_data = request.data 

    report_type = request.data.get('report_type', None)

    if report_type not in ['class_course', 'department', 'admin']:
        return Response({'message': 'Specify Report Type'}, status=HTTP_400_BAD_REQUEST)

    general_setting = GeneralSetting.objects.first()

    academic_year = request_data.get('year', general_setting.academic_year)
    semester = request_data.get('semester', general_setting.current_semester)


    #generate a prefix for the resultant file name
    ys_prefix = f'{academic_year}0{semester}'


    report = None

    if report_type == 'class_course':
        class_course = None
        try:
            class_course = ClassCourse.objects.get(id=request_data.get('id', None))
        except ClassCourse.DoesNotExist:
            return Response({'message': 'Requested Class does not exist.'}, status=HTTP_400_BAD_REQUEST)

        report = course_eval_report.CourseEvalExcelReport(class_course)

        pass

    elif report_type == 'department':
        department = None 

        try:
            department = Department.objects.get(id=request_data.get('id', None))
        except Department.DeosNotExist:
            return Response({'message': 'Requested Department does not exist'})

        report = departmental_report.DepartmentalExcelReport(department, semester=semester, year=academic_year)
        pass 

    else: #when the report type is equal to admin
        #todo: add a condition here to check for the user's permission before file is generated
        report = admin_report.AdminExcelReport(semester=semester, year=academic_year)
        pass  


    report_file = report.save() #all three report file generators have 'save' method

    return Response(report_file.toMap(request))


@api_view(['GET'])
def downloadFile(request, file_url):

    report_file = ReportFile.objects.get(file_url=file_url)

    return FileResponse(
        report_file.file, 
        as_attachment=True, 
        filename=f'{report_file.file_name}.{report_file.file_type}'
    )



#returns the list of all report_file objects in the database.
@api_view(['GET'])
def get_all_files(request):
    report_files = ReportFile.objects.all()
    return Response([report_file.toMap(request) for report_file in report_files])

