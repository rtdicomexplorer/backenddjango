import logging
import requests

from api.serializers import FhirServerSerializers

logger = logging.getLogger('backenddjango')

class FhirCommunication:

     def query_resource(self,request):
       
        print('POST FHIR  Search request incoming')
        logger.debug("POST FHIR  Qery request incoming")
        try:
            dcm_server = request.data['remoteserver']
            payload = request.data['payload']
            servserializer = FhirServerSerializers(data=dcm_server)
            remote_scp = servserializer.initial_data      
            host = remote_scp['host']
            url = host+payload['keyresource']
            header = { 'Content-Type': 'application/json'}
            return requests.get(url=f'{url}', headers=header, verify=False)

        except Exception as e:
            logger.exception('An error occurred: %s', e)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)

