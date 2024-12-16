from .views import login, signup, delete, users, test_auth_token

from django.urls import path

urlpatterns=[
    path ('login/', login),
    path ('signup/', signup),
    path ('users', users),
    path ('delete/', delete),
    path('test_auth_token/',test_auth_token),
]