from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework import status
from django.http import  HttpResponse
from api.dcm_comm_class import DcmCommunication
from django.conf import settings
from .dicom_comm_commands import get_binaryimage, get_dcm_filelist, get_base64image
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
        value_error =  f'An error occurred: {e.args[0]}'
        __logger.exception(value_error)
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST})


#C-FIND command
@api_view(['POST'])
def find_command(request):
    try:      
        dcm_com = DcmCommunication()
        result = dcm_com.execute_c_find(request)
        message = result['message']
        if message == '':
            items_found = result['response']          
            return JsonResponse({'data': items_found , 'status': status.HTTP_200_OK,'sessionkey':dcm_com.uid})
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})

    except Exception as e:
        value_error =  f'An error occurred: {e.args[0]}'
        __logger.exception(value_error)
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})


#C-GET command
@api_view(['POST'])
def get_command(request):
    try:      
        dcm_com = DcmCommunication()
        result = dcm_com.execute_c_get(request)
        message = result['message']
        if message == '':
            items_found = result['response']          
            return JsonResponse({'data': items_found , 'status': status.HTTP_200_OK, 'sessionkey':dcm_com.uid})
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})

    except Exception as e:
        value_error =  f'An error occurred: {e.args[0]}'
        __logger.exception(value_error)
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})


#C-MOVE command
@api_view(['POST'])
def move_command(request):
    try:      
        dcm_com = DcmCommunication()
        result = dcm_com.execute_c_move(request)
        message = result['message']
        if message == '':
            items_found = result['response']          
            return JsonResponse({'data': items_found , 'status': status.HTTP_200_OK,'sessionkey':dcm_com.uid})
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})

    except Exception as e:
        value_error =  f'An error occurred: {e.args[0]}'
        __logger.exception(value_error)
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})





#C-STORE command
@api_view(['POST'])
def store_command(request):
    try:      
        settings.DATA_UPLOAD_MAX_NUMBER_FILES = None
        dcm_com = DcmCommunication()
        result = dcm_com.execute_c_store(request)
        message = result['message']
        if message == '':
            items_found = result['response'] 
            if 'fhir'in result:        
                return JsonResponse({'data': items_found ,'fhir':result['fhir'], 'status': status.HTTP_200_OK,'sessionkey':dcm_com.uid})
            else:
                return JsonResponse({'data': items_found ,'status': status.HTTP_200_OK,'sessionkey':dcm_com.uid})
            
        else:
            return JsonResponse({'message': message , 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})

    except Exception as e:
        value_error =  f'An error occurred: {e.args[0]}'
        __logger.exception(value_error)
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST,'sessionkey':dcm_com.uid})



@api_view(['POST'])
def get_binary(request):
    try:            
        return HttpResponse(get_binaryimage(request), content_type='application/octet-stream')
    except Exception as e:
        value_error =  f'An error occurred: {e.args[0]}'
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST})

@api_view(['POST'])
def get_base64(request):
    try:      
        return JsonResponse( {'data': get_base64image(request),'status': status.HTTP_200_OK })

    except Exception as e:
        value_error =  f'An error occurred: {e.args[0]}'
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST})


@api_view(['POST'])
def get_dicom_file_list(request):

    try:      
        file_to_send = get_dcm_filelist(request)
        return JsonResponse( {'data': file_to_send ,'status': status.HTTP_200_OK })
    except Exception as e:
        value_error =  f'An error occurred: {e.args[0]}'
        return JsonResponse( {'message': value_error, 'status': status.HTTP_400_BAD_REQUEST})