from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializers(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['id', 'email', 'password', 'name', 'is_superuser', 'is_staff', 'is_active']