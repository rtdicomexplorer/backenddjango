from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework import status

from api.dcm_comm_class import DcmCommunication
from pynetdicom import debug_logger
from django.conf import settings
import logging
__logger = logging.getLogger('backenddjango')

#C-ECHO command
@api_view(['POST'])
def echo_command(request):  
    try:
        dcm_com = DcmCommunication()
        result = dcm_com.execute_echo(request)
        rsp_status =   status.HTTP_200_OK
        if result['status'] == False:
            rsp_status = status.HTTP_503_SERVICE_UNAVAILABLE  
        return JsonResponse( {'message': result['message'], 'status': rsp_status})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        return JsonResponse( {'message': e, 'status': status.HTTP_400_BAD_REQUEST})


#C-FIND command
@api_view(['POST'])
def find_command(request):
    try:      
        dcm_com = DcmCommunication()
        result = dcm_com.execute_c_find(request)
        message = result['message']
        if message == '':
            items_found = result['response']          
            return JsonResponse({'data': items_found , 'status': status.HTTP_200_OK})
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST})

    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        return JsonResponse( {'message': e, 'status': status.HTTP_400_BAD_REQUEST})




#C-GET command
@api_view(['POST'])
def get_command(request):
    try:      
        dcm_com = DcmCommunication()
        result = dcm_com.execute_c_get(request)
        message = result['message']
        if message == '':
            items_found = result['response']          
            return JsonResponse({'data': items_found , 'status': status.HTTP_200_OK})
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST})

    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        return JsonResponse( {'message': e, 'status': status.HTTP_400_BAD_REQUEST})