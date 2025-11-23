from django.shortcuts import render
from django.http import HttpResponse

from .models import Student

from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.


@api_view(['GET', 'POST'])
def generate_report(request):

    return Response()