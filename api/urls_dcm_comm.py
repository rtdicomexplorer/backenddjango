from .views_dcm_comm import echo_command, find_command,get_command,store_command,move_command, get_binary, get_dicom_file_list, get_base64
from django.urls import path

urlpatterns=[
    path('echo/', echo_command),
    path('find/', find_command),
    path('get/', get_command),
    path('move/', move_command),
    path('store/', store_command),
    path('get/filelist/', get_dicom_file_list),
    path('get/binary/', get_binary),
    path('get/base64/', get_base64),
]