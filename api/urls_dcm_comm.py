from .views_dcm_comm import echo_command, find_command,get_command,get_binary, get_dicom_file_list
from django.urls import path

urlpatterns=[
    path('echo/', echo_command),
    path('find/', find_command),
    path('get/', get_command),
    path('get/filelist/', get_dicom_file_list),
    path('get/binary/', get_binary),
]