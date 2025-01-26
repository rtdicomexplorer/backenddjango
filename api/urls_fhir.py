from .views_fhir_server import addserver, delete, servers, server, update
from django.urls import path

urlpatterns=[
    path('servers',servers),
    path('server/add/', addserver),
    path('server/<int:pk>', server),
    path('server/delete/<int:pk>', delete),
    path('server/update/<int:pk>', update),
    
]