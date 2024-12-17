from django.contrib import admin

from .models import CustomUser, FhirServer

admin.site.register(CustomUser)
admin.site.register(FhirServer)
# Register your models here.
