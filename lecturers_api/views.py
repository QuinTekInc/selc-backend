
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.status import *

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from selc_core.models import Lecturer, Department, ClassCourse


# Create your views here.

@api_view(['POST'])
def loginLecturer(request):

    username = request.data.get('username')
    password = request.data.get('password')


    user = None

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'message': 'Incorrect username or password'})
    

    if not user.check_password(password):
        return Response({'message': 'Incorrect username or password'}, status=HTTP_401_UNAUTHORIZED)
    

    lecturer = Lecturer.objects.get(user=user)
    
    return Response(lecturer.toMap())



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logoutLecturer(request):
    logout(request)
    return Response({'message': f'{request.user.username} logged out'})