from django.shortcuts import render
from django.http import HttpResponse

from .models import Student

from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.


@api_view(['GET', 'POST'])
def generate_report(request):

    request_data = request.data

    report = None

    #check it is a class_course
    if 'class_course' in request_data:
        pass

    elif 'admin_report' in request_data:
        pass

    elif 'department_report' in request_data:
         pass

    return Response({'message': 'this functionality is yet to be implemented'})