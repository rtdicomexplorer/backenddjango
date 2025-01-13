from .views_dcm_server import servers, addserver, server, update, delete
from django.urls import path

urlpatterns=[
    path('servers',servers),
    path('server/add',addserver),
    path('server/<int:pk>', server),
    path('server/delete/<int:pk>', delete),
    path('server/update/<int:pk>', update),
]