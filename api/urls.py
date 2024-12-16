from .views import login, signup, delete, users

from django.urls import path

urlpatterns=[
    path ('login/', login),
    path ('signup/', signup),
    path ('users', users),
    path ('delete/', delete),
]