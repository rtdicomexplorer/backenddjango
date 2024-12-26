from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import CustomUserSerializers
from rest_framework.authtoken.models import Token

from .models import CustomUser
import base64
from django.conf import settings
 

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
        token = Token.objects.create(user=user)
        return JsonResponse({'message': 'user created', 'user': serializer.data, 'token':token.key})
    return JsonResponse(serializer.errors, status=status.HTTP_200_OK)

#LOGIN
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def login(request):
    print('POST login request incoming')
    user = get_object_or_404(CustomUser, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return JsonResponse({"message": "missing user", "status":status.HTTP_404_NOT_FOUND})   
    serializer = CustomUserSerializers(user)
    token, created = Token.objects.get_or_create(user=user)
    return JsonResponse({'message': "user logged in", 'user': serializer.data, 'token':token.key, 'created': created})


#user list
@api_view(['GET'])
#@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated,IsAdminUser])
def users(request):
    print('GET user list request incoming')
    userList = CustomUser.objects.values()
    return JsonResponse({'users list: ': list(userList)})


#GET user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user(request, pk):
    print('GET user request incoming')
    user = get_object_or_404(CustomUser, pk=pk)
    if not user:
         return JsonResponse({"message": "missing user", "status":status.HTTP_404_NOT_FOUND})  
    
    img_url = user.image.url

    if user.image.url.startswith('/') or user.image.url.startswith("\\"):
        img_url = user.image.url[1:]

    img_path = settings.BASE_DIR / img_url
    print('url',img_path)

    img_file = open(img_path, "rb")
    img64 =  base64.b64encode(img_file.read()).decode('utf-8')
    return JsonResponse({"message": img64, "status":status.HTTP_200_OK})


#delete user
@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser])
def delete(request,pk):
    print('DELETE user request incoming')
    user = get_object_or_404(CustomUser, pk=pk)
    if not user:
         return JsonResponse({"message": "missing user", "status":status.HTTP_404_NOT_FOUND})  
    user.delete()
    return JsonResponse({"user data": user, "status":status.HTTP_200_OK})



@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_auth_token(request):  
    return JsonResponse({'message': 'Test passed for', 'user': request.user.email})

# Create your views here.
