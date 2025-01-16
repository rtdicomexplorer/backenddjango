from .views_dcm_comm import echo_command, find_command
from django.urls import path

urlpatterns=[
    path('echo/', echo_command),
    path('find/', find_command),
]