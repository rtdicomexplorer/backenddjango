from .views_fhir import create, delete, servers
from django.urls import path

urlpatterns=[
    path ('create/', create),
    path('servers',servers),
    path('delete/<int:pk>', delete)
]