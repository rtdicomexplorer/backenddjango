from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import CustomUserSerializers

from .models import CustomUser

#SIGNUP
@api_view(['POST'])
def signup(request):
    print('POST signup request incoming')
    serializer = CustomUserSerializers(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = CustomUser.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        return JsonResponse({'message': 'user created', 'user': serializer.data})
    return JsonResponse(serializer.errors, status=status.HTTP_200_OK)

#LOGIN
@api_view(['POST'])
def login(request):
    print('POST login request incoming')
    user = get_object_or_404(CustomUser, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return JsonResponse({"message": "missing user", "status":status.HTTP_404_NOT_FOUND})
    
    serializer = CustomUserSerializers(user)
    return JsonResponse({'message': "user logged in", 'user': serializer.data})


#user list
@api_view(['GET'])
def users(request):
    print('GET user list request incoming')
    userList = CustomUser.objects.values()
    return JsonResponse({'users list: ': list(userList)})

#delete user
@api_view(['POST'])
def delete(request):
    print('POST delete request incoming')
    user = get_object_or_404(CustomUser, id=request.data['id'])
    if not user:
         return JsonResponse({"message": "missing user", "status":status.HTTP_404_NOT_FOUND})  
    if user.is_superuser:
        return JsonResponse({"message": "Unable to delete superuser", "status":status.HTTP_401_UNAUTHORIZED})  
    user.delete()
    return JsonResponse({"message": "user removed "+user.email, "status":status.HTTP_200_OK})



# Create your views here.
