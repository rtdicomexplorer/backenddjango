from django.contrib import admin

from .models import CustomUser, FhirServer, DicomServer, LocalConfig

admin.site.register(CustomUser)
admin.site.register(FhirServer)
admin.site.register(DicomServer)
admin.site.register(LocalConfig)
# Register your models here.
