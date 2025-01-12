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


#GET server
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def server(request, pk):
    print('GET server request incoming')
    dcm_server = get_object_or_404(DicomServer, pk=pk)
    if not dcm_server:
         return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
    serializer = DicomServerSerializers(dcm_server)

    return JsonResponse({"data": serializer.data, "status":status.HTTP_200_OK})

#UPDATE server
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, pk):
    print('Update server request incoming')
    dcm_server = get_object_or_404(DicomServer, pk=pk)
    if not dcm_server:
         return JsonResponse({"message": "missing server", "status":status.HTTP_404_NOT_FOUND})  
    dcm_server.aetitle = request.data['aetitle']
    dcm_server.port = request.data['port']
    dcm_server.description = request.data['description']
    dcm_server.host = request.data['host']
    dcm_server.save()
    return JsonResponse({'message': dcm_server.id, 'status': status.HTTP_201_CREATED})

#addserver
@api_view(['POST'])
def addserver(request):
    print('POST add server request incoming')
    servserializer = DicomServerSerializers(data=request.data)
    if servserializer.is_valid(raise_exception=True):
        try:
            
            aetitle = servserializer.validated_data['aetitle']
            servserializer.save()
            server = DicomServer.objects.get(aetitle=request.data['aetitle'])
            server.save()
            return JsonResponse({'data': server.id, 'status': status.HTTP_201_CREATED})
        except Exception as e:
            print (e)
    error = str(list(servserializer.errors.values())[0][0])
    return JsonResponse( {'message': error, 'status': status.HTTP_400_BAD_REQUEST})