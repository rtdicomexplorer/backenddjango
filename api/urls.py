from .views import login, signup, delete, users, test_auth_token, user, signupprofileavatar, update, config, config_update
from django.urls import path

from rest_framework_simplejwt.views import( TokenObtainPairView, TokenRefreshView)


urlpatterns=[
    path ('login/', login),
    path ('signup/', signup),
    path ('signupavatar/<int:pk>', signupprofileavatar),
    path ('users', users),
    path('user/<int:pk>', user),
    path('user/update/<int:pk>', update),
    path ('user/delete/<int:pk>', delete),
    path('test_auth_token/',test_auth_token),
    path('token/',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh',TokenRefreshView.as_view(), name='token_refresh'),
    path ('config', config),
    path ('config/update/<int:pk>', config_update),
]