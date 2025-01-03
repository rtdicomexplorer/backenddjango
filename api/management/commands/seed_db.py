from django.core.management.base import BaseCommand
from api.models import CustomUser,FhirServer
import os
from dotenv import load_dotenv
class Command(BaseCommand):
    help = 'Creates databes seed data'

    def handle(self, *args, **kwargs):
        # get or create superuser
        load_dotenv(override=True)
        login_email = os.getenv('LOGIN_EMAIL', default="test@test.com")
        login_password =  os.getenv('LOGIN_PASSWORD', default="admin")
        login_name = os.getenv('LOGIN_NAME', default='test')
        user = CustomUser.objects.filter(email=login_email).first()
        if not user:
            user = CustomUser.objects.create_superuser(email=login_email, password=login_password,name=login_name)
        fhirname = os.getenv('FHIR_NAME', default="hapi_demo")
        fhirhost = os.getenv('FHIR_HOST', default="https://hapi.fhir.org/baseR4/")
        fhirdescription = os.getenv('FHIR_DESCR', default="hapi fhir demo which supports R4")
        # server = FhirServer.objects.filter(name=fhirname,host=fhirhost)
        # if not server:
            #server =  FhirServer(name= fhirname, host = fhirhost, description = fhirdescription)    
        result = FhirServer.objects.get_or_create(name= fhirname, host = fhirhost, description = fhirdescription)
        print (result)