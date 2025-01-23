from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework import status
from django.http import  HttpResponse
from api.dcm_comm_class import DcmCommunication
from pynetdicom import debug_logger
from django.conf import settings
from .dicom_comm_commands import get_binaryimage, get_dcm_filelist
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


@api_view(['POST'])
def get_binary(request):
     
    try:      
        
        file_to_send = get_binaryimage(request)
        if file_to_send != '':
            return HttpResponse(open(file_to_send, 'rb'), content_type='application/octet-stream')
        else:
            return HttpResponse({'message': 'file not found' , 'status': status.HTTP_400_BAD_REQUEST}, content_type='application/json')

    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        return JsonResponse( {'message': e, 'status': status.HTTP_400_BAD_REQUEST})
    

@api_view(['POST'])
def get_dicom_file_list(request):
    try:      
        file_to_send = get_dcm_filelist(request)
        return JsonResponse( {'data': file_to_send ,'status': status.HTTP_200_OK })
    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        return JsonResponse( {'message': e, 'status': status.HTTP_400_BAD_REQUEST})