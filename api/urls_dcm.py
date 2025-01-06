from .views_dcm import servers
from django.urls import path

urlpatterns=[
    path('servers',servers),
]