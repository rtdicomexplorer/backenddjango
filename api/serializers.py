from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, FhirServer

class CustomUserSerializers(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['id', 'email', 'password', 'name', 'is_superuser', 'is_staff', 'is_active']


class FhirServerSerializers(serializers.ModelSerializer):
    class Meta(object):
        model = FhirServer
        fields = ['name', 'description', 'host', 'port']




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        return token