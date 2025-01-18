from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import DicomServerSerializers
from pynetdicom import debug_logger
from django.conf import settings
from .dicom_comm_commands import execute_echo, execute_c_find
#debug_logger()

@api_view(['POST'])
def echo_command(request):
    print('POST echo command request incoming') 
    
    try:
        servserializer = DicomServerSerializers(data=request.data)
        remote_scp = servserializer.initial_data
        local_ae = settings.LOCAL_AET
        response  = execute_echo(local_ae,remote_scp)
        rsp_status =   status.HTTP_200_OK
        if response['status'] == False:
            rsp_status = status.HTTP_503_SERVICE_UNAVAILABLE  
        return JsonResponse( {'message': response['message'], 'status': rsp_status})
    except Exception as e:
        print (e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})


#find command
@api_view(['POST'])
def find_command(request):
 
    print('POST: find command request incoming') 
    try:
       
        dcm_server = request.data['remotescp']
        query_retrieve_level=request.data['queryretrievelevel']
        payload = request.data['payload']
        servserializer = DicomServerSerializers(data=dcm_server)
        remote_scp = servserializer.initial_data      
        local_ae = settings.LOCAL_AET
        result  = execute_c_find(local_ae,remote_scp, query_retrieve_level,payload)
        message = result['message']
        if message == '':
            items_found = result['response']   
            return JsonResponse({'data': items_found , 'status': status.HTTP_200_OK})
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST})

    except Exception as e:
        print (e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})




