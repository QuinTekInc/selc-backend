
from django.http import FileResponse
from django.contrib.auth.models import Group
from django.db.models import Q as Query

from admin_api.decorators import requires_roles
from .models import Department, ClassCourse, ReportFile, GeneralSetting
from .models import Lecturer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import *

from .report_generators import course_eval_report, admin_report, departmental_report

# Create your views here.

@api_view(['POST'])
def generate_report(request):

    #NOTE: format of the request data for generating reports
    """
    {
        'report_type': 'admin' or 'department' or 'class_course',
        'id': cc_id or department_id   note that admin reports do not require id's,
        'semester': academic_semester,
        'year': academic_year,
        'file_type: '.pdf' or '.xlsx' (default is '.xlsx')
    }
    """

    request_data = request.data 

    report_type = request_data.get('report_type', None)

    if report_type not in ['class_course', 'department', 'admin']:
        return Response({'message': 'Specify Report Type'}, status=HTTP_400_BAD_REQUEST)

    general_setting = GeneralSetting.objects.first()

    academic_year = request_data.get('year', general_setting.academic_year)
    semester = request_data.get('semester', general_setting.current_semester)


    #generate a prefix for the resultant file name
    ys_prefix = f'{academic_year}0{semester}'


    file_type = request_data.get('file_type', '.xlsx')


    report = None

    if report_type == 'class_course':
        class_course = None
        try:
            class_course = ClassCourse.objects.get(id=request_data.get('id', None))
        except ClassCourse.DoesNotExist:
            return Response({'message': 'Requested Class does not exist.'}, status=HTTP_400_BAD_REQUEST)

        report = course_eval_report.CourseEvalExcelReport(class_course)

        #note that PDF report is exclusive to only Class Course Evaluations. 
        if file_type == '.pdf': 
            report = course_eval_report.CourseEvalPdfReport(class_course)

        pass

    elif report_type == 'department':
        department = None 

        try:
            department = Department.objects.get(id=request_data.get('id', None))
        except Department.DoesNotExist:
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
def get_all_files(request): #should be renamed to get files

    user = request.user

    if user is None: 
        return Response({'message': 'Login required'}, status=HTTP_403_FORBIDDEN)

    #check the role of the user
    lecturer = Lecturer.objects.filter(user=user)

    if lecturer.exists():

        lecturer = lecturer.first()
        l_class_courses = ClassCourse.objects.filter(lecturer=lecturer)

        cc_file_names = [cc.getSavableReportFileName() for cc in l_class_courses]
        
        reduced_file_names = [fccn[0: fccn.rindex('.')] for fccn in cc_file_names]

        file_names = cc_file_names + reduced_file_names#if the file name contains the lecturer's name.

        query = (Query(file_name__in=file_names) | Query(file_name__icontains=lecturer.getFullName()))
            
        report_files = ReportFile.objects.filter(query)

        #print('REPORT FILES FOUND FOR LECTURER: ', report_files.count())
        
        return Response([report_file.toMap(request) for report_file in report_files])


    report_files = ReportFile.objects.all()
    
    return Response([report_file.toMap(request) for report_file in report_files])





