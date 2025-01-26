from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import FhirServerSerializers
from .models import FhirServer
import logging
__logger = logging.getLogger('backenddjango')


#list
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def servers(request):
    print('GET FHIR server list request incoming')
    __logger.info("GET server list request incoming")

    try:
        
        serverList = FhirServer.objects.values()
        serializer = FhirServerSerializers(serverList, many = True)
        __logger.debug("FHIR server list found!")
        return JsonResponse({'data': serializer.data,  "status":status.HTTP_200_OK})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)

#GET server
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def server(request, pk):
    __logger.debug("GET FHIR server request incoming")
    print('GET server request incoming')
    try:

        fhir_server = get_object_or_404(FhirServer, pk=pk)
        if not fhir_server:
            __logger.debug("FHIR server not found!")
            return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
        serializer = FhirServerSerializers(fhir_server)
        __logger.debug("FHIR server "+fhir_server.name+" found!")
        return JsonResponse({"data": serializer.data, "status":status.HTTP_200_OK})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        
        
#UPDATE server
@api_view(['PUT'])
@permission_classes([IsAuthenticated,IsAdminUser])
def update(request, pk):
    print('UPDATE FHIR server request incoming')
    __logger.debug("UPDATE FHIR server request incoming")
    try:

        fhir_server = get_object_or_404(FhirServer, pk=pk)
        if not fhir_server:
            return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
        fhir_server.name = request.data['name']
        fhir_server.port = request.data['port']
        fhir_server.description = request.data['description']
        fhir_server.host = request.data['host']
        fhir_server.save()
        __logger.debug("FHIR server "+fhir_server.aetitle+" updated!")
        return JsonResponse({'message': fhir_server.id, 'status': status.HTTP_201_CREATED})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)       
#create
#addserver
@api_view(['POST'])
def addserver(request):
    print('POST add server request incoming')
    __logger.debug("POST add server request incoming")
    servserializer = FhirServerSerializers(data=request.data)
    if servserializer.is_valid(raise_exception=True):
        try:
            host = servserializer.validated_data['host']
            servserializer.save()
            fhir_server = FhirServer.objects.get(host=request.data['host'])
            fhir_server.save()
            __logger.debug("FHIR server "+fhir_server.aetitle+" added!")
            return JsonResponse({'data': fhir_server.id, 'status': status.HTTP_201_CREATED})
        except Exception as e:
            __logger.exception('An error occurred: %s', e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})



#delete SERVER
@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser])
def delete(request,pk):
    print('DELETE FHIR server request incoming')
    __logger.debug("DELETE DICOM server request incoming")
    try:
        fhir_server = get_object_or_404(FhirServer, pk=pk)
        if not fhir_server:
            __logger.debug("missing server")
            return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
        fhir_server.delete()
        __logger.debug("FHIR server "+fhir_server.name+" deleted!")
        return JsonResponse({"message":"server deleted" , "status":status.HTTP_200_OK})
    except Exception as e:
        __logger.exception('An error occurred: %s', e)

