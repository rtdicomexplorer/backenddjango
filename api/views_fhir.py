from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from rest_framework import status
from .serializers import FhirServerSerializers
from .models import FhirServer



#create
@api_view(['POST'])
def create(request):
    print('POST create fhir request incoming')
    serializer = FhirServerSerializers(data=request.data)
    if serializer.is_valid():
        serializer.save()
        server = FhirServer.objects.get(name=request.data['name'])
        if server is not None:
            return JsonResponse({'message': 'server created', 'name': serializer.data['name']})
    return JsonResponse(serializer.errors, status=status.HTTP_200_OK)

#user list
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def servers(request):
    print('GET server list request incoming')
    userList = FhirServer.objects.values()
    return JsonResponse({'server list: ': list(userList)})


#delete user
@api_view(['DELETE'])
def delete(request, pk):
    print('POST delete request incoming')
    server = get_object_or_404(FhirServer, pk=pk)
    if not server:
         return JsonResponse({"message": "missing product", "status":status.HTTP_404_NOT_FOUND})  
    server.delete()
    return JsonResponse({"message": "server removed "+server.name, "status":status.HTTP_200_OK})