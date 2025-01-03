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
import os
from django.core.files.storage import FileSystemStorage  

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
        return JsonResponse({'message': user.id, 'status': status.HTTP_201_CREATED})
    
    error = str(list(serializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})



@api_view(['POST'])
def signupprofileavatar(request, pk):
    print('POST signup-profile photo request incoming', pk)
    user = get_object_or_404(CustomUser, pk=pk)
    if not user:
         return JsonResponse({"message": "missing user", "status":status.HTTP_404_NOT_FOUND})  
    print ("User found:", user)
    return handle_uploaded_file(request, user)


def handle_uploaded_file(request, user):
    key ='file'
    if key in request.FILES:
        files = request.FILES.getlist(key)
        saveFolder = os.path.join(settings.MEDIA_AVATAR)
        for file in files:
            try:
                FileSystemStorage(location=saveFolder).save(file.name, file)
                user.image = settings.AVATARS_URL+file.name #  (os.path.join(saveFolder, file.name),File().read())
                user.save()
                return JsonResponse({'message': 'avatar uploaded'}, status=status.HTTP_201_CREATED) 
            except Exception as e:
                return JsonResponse({'message': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)   


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
    return JsonResponse({'message': "user logged in", 'user': serializer.data, 'token':token.key, 'created': created,'status': status.HTTP_201_CREATED})


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
    
    img_url = 'media/default/user.png'
    try:
        if user.image.url.startswith('/') or user.image.url.startswith("\\"):
            img_url = user.image.url[1:]
        else:
            img_url = user.image.url
    except:
        img_url = 'media/default/user.png'

    img_path = settings.BASE_DIR / img_url
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
