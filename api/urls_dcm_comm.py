from .views_dcm_comm import echo_command, find_command,get_command
from django.urls import path

urlpatterns=[
    path('echo/', echo_command),
    path('find/', find_command),
    path('get/', get_command),
]