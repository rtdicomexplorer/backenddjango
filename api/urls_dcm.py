from .views_dcm import servers, addserver, server, update
from django.urls import path

urlpatterns=[
    path('servers',servers),
    path('server/add',addserver),
    path('server/<int:pk>', server),
    path('server/update/<int:pk>', update),
]