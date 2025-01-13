from .views_dcm_comm import echo_command
from django.urls import path

urlpatterns=[
    path('echo/', echo_command),
]