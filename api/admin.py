from django.contrib import admin

from .models import CustomUser, FhirServer, DicomServer

admin.site.register(CustomUser)
admin.site.register(FhirServer)
admin.site.register(DicomServer)
# Register your models here.
