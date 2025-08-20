
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import *

from functools import wraps


def ensure_active_user(function):

    def wrapper(request):

        if  request.user is None:
            return Response({'message': 'Persmission denied: account does not exist.'}, status=HTTP_404_NOT_FOUND)
        
        user: User = request.user
        
        if user.username.strip() == '':
            return Response({'message': 'Permission Denied: Your account does not exist'}, status=HTTP_403_FORBIDDEN)
        
        if not user.is_authenticated:
            return Response({'message': 'Permission denied: Login required'}, status=HTTP_403_FORBIDDEN)
        

        if not user.is_active:
            return Response({'message': 'Permission denied: Account must be marked as active.'}, status=HTTP_403_FORBIDDEN)
        
        return function(request)
    
    return wrapper
        



def requires_superuser(view_function):

    @wraps(view_function)
    @ensure_active_user
    def wrapper(request):

        user: User = request.user
    

        if not user.is_superuser and  not user.groups.filter(name='superuser').exists():
            return Response({'message': 'Permission denied: You must have super user privileges'}, status=HTTP_403_FORBIDDEN)

        
        return view_function(request)

    return wrapper





def requires_roles(allowed_roles: list):
    
    def decorator(view_function):

        @wraps(view_function)
        @ensure_active_user
        def wrapper(request, *args, **kwargs):
            user: User = request.user
            user_groups = user.groups.all()

            if not user_groups.exists():
                return Response({'message': 'Permission Denied: You do not belong to any group.'}, status=HTTP_403_FORBIDDEN)

            user_group_names = [group.name for group in user_groups]
            if not any(role in user_group_names for role in allowed_roles):
                return Response({'message': 'Permission Denied: You do not have the required privileges.'}, status=HTTP_403_FORBIDDEN)

            return view_function(request, *args, **kwargs)
        
        return wrapper
    
    return decorator
