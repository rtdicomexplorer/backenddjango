from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import DicomServerSerializers
from .models import DicomServer

#server list
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def servers(request):
    print('GET server list request incoming')
    serverList = DicomServer.objects.values()
    serializer = DicomServerSerializers(serverList, many = True)
    return JsonResponse({'data': serializer.data,  "status":status.HTTP_200_OK})