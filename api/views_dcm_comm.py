from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import DicomServerSerializers
from .models import DicomServer


#addserver
@api_view(['POST'])
def echo_command(request):
    print('POST echo command request incoming')
    servserializer = DicomServerSerializers(data=request.data)



    if servserializer.is_valid(raise_exception=True):
        try:
            
            aetitle = servserializer.validated_data['aetitle']
            host = servserializer.validated_data['host']
            port = servserializer.validated_data['port']
            return JsonResponse({'result': 'true' , 'status': status.HTTP_200_OK})
        except Exception as e:
            print (e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})

