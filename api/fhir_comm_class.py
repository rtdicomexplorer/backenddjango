import logging
import requests
import urllib3
urllib3.disable_warnings()
logger = logging.getLogger('backenddjango')

class FhirCommunication:    

    def query_resource(self,request):
       
        print('POST FHIR  Search request incoming')
        logger.debug("POST FHIR  Qery request incoming")
        try:
            url = request.data['url']
            header = { 'Content-Type': 'application/json'}
            return requests.get(url=f'{url}', headers=header, verify=False)

        except Exception as e:
            logger.exception('An error occurred: %s', e)
            raise  Exception(e)

