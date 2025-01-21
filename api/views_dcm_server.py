from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import DicomServerSerializers
from .models import DicomServer
import logging
__logger = logging.getLogger('backenddjango')
#server list
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def servers(request):
    print('GET DICOM server list request incoming')
    __logger.info("GET server list request incoming")

    try:
        
        serverList = DicomServer.objects.values()
        serializer = DicomServerSerializers(serverList, many = True)
        __logger.debug("DICOM server list found!")
        return JsonResponse({'data': serializer.data,  "status":status.HTTP_200_OK})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        
        


#GET server
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def server(request, pk):
    __logger.debug("GET DICOM server request incoming")
    print('GET server request incoming')
    try:

        dcm_server = get_object_or_404(DicomServer, pk=pk)
        if not dcm_server:
            __logger.debug("DICOM server not found!")
            return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
        serializer = DicomServerSerializers(dcm_server)
        __logger.debug("DICOM server "+dcm_server.aetitle+" found!")
        return JsonResponse({"data": serializer.data, "status":status.HTTP_200_OK})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)

#UPDATE server
@api_view(['PUT'])
@permission_classes([IsAuthenticated,IsAdminUser])
def update(request, pk):
    print('UPDATE server request incoming')
    __logger.debug("UPDATE DICOM server request incoming")
    try:

        dcm_server = get_object_or_404(DicomServer, pk=pk)
        if not dcm_server:
            return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
        dcm_server.aetitle = request.data['aetitle']
        dcm_server.port = request.data['port']
        dcm_server.description = request.data['description']
        dcm_server.host = request.data['host']
        dcm_server.save()
        __logger.debug("DICOM server "+dcm_server.aetitle+" updated!")
        return JsonResponse({'message': dcm_server.id, 'status': status.HTTP_201_CREATED})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)


#addserver
@api_view(['POST'])
def addserver(request):
    print('POST add server request incoming')
    __logger.debug("POST add server request incoming")
    servserializer = DicomServerSerializers(data=request.data)
    if servserializer.is_valid(raise_exception=True):
        try:
            aetitle = servserializer.validated_data['aetitle']
            servserializer.save()
            dcm_server = DicomServer.objects.get(aetitle=request.data['aetitle'])
            dcm_server.save()
            __logger.debug("DICOM server "+dcm_server.aetitle+" added!")
            return JsonResponse({'data': dcm_server.id, 'status': status.HTTP_201_CREATED})
        except Exception as e:
            __logger.exception('An error occurred: %s', e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})


#delete SERVER
@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser])
def delete(request,pk):
    print('DELETE server request incoming')
    __logger.debug("DELETE DICOM server request incoming")
    try:

        dcm_server = get_object_or_404(DicomServer, pk=pk)
        if not dcm_server:
            __logger.debug("missing server")
            return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
        dcm_server.delete()
        __logger.debug("DICOM server "+dcm_server.aetitle+" deleted!")
        return JsonResponse({"message":"server deleted" , "status":status.HTTP_200_OK})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)

