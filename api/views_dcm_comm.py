from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import DicomServerSerializers
from .models import DicomServer
from pynetdicom import AE,debug_logger

from django.conf import settings

from .dicom_comm_commands import execute_echo, execute_c_find
debug_logger()
#echo command
@api_view(['POST'])
def echo_command(request):
    print('POST echo command request incoming') 
    
    try:
        servserializer = DicomServerSerializers(data=request.data)
        remote_scp = servserializer.initial_data
        local_ae = settings.LOCAL_AET
        assoc = execute_echo(local_ae,remote_scp)

        # ae = AE(aetitle)
        # ae.add_requested_context("1.2.840.10008.1.1")
        # assoc = ae.associate(host, port)
        if assoc.is_established:
            print("Association established with Echo SCP!")
            assoc.release()
            return JsonResponse({'result': 'true' , 'status': status.HTTP_200_OK})
        else:
            # Association rejected, aborted or never connected
            print("Failed to associate")
            return JsonResponse({'result': 'false' , 'status': status.HTTP_403_FORBIDDEN})
    except Exception as e:
        print (e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})


#echo command
@api_view(['POST'])
def find_study_command(request):
    print('POST echo command request incoming') 
    
    try:
        dcm_server = request.data['remotescp']
        payload = request.data['payload']
        servserializer = DicomServerSerializers(data=dcm_server)
        remote_scp = servserializer.initial_data      
        local_ae = settings.LOCAL_AET
        result  = execute_c_find(local_ae,remote_scp, payload)
        
        message = result['message']
        if message == '':
            study = result['response']   
            return JsonResponse({'data': study , 'status': status.HTTP_200_OK})
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST})

    except Exception as e:
        print (e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})




