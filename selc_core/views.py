from django.shortcuts import render
from django.http import HttpResponse

from .models import Student

# Create your views here.


def getStudents():

    students = Student.objects.all()
    return HttpResponse('<p> Hello motherfucking students </p>')