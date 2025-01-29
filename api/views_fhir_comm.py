from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http.response import JsonResponse
from rest_framework import status
from django.http import  HttpResponse
from api.fhir_comm_class import FhirCommunication

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_resource (request):
    try:      
        fhir_com = FhirCommunication()
        response = fhir_com.query_resource(request)
        return HttpResponse(response)
    except Exception as e:
        return JsonResponse( {'message': e, 'status': status.HTTP_400_BAD_REQUEST})

