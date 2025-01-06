from .views_dcm import servers, addserver
from django.urls import path

urlpatterns=[
    path('servers',servers),
    path('server/add',addserver),
]