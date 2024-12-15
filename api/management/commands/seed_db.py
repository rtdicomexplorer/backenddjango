from django.core.management.base import BaseCommand
from api.models import CustomUser
import os
import os
from dotenv import load_dotenv
class Command(BaseCommand):
    help = 'Creates databes seed data'

    def handle(self, *args, **kwargs):
        # get or create superuser
        load_dotenv(override=True)
        login_email = os.getenv('LOGIN_EMAIL', default="test@test.com")
        login_password =  os.getenv('LOGIN_PASSWORD', default="admin")
        user = CustomUser.objects.filter(email=login_email).first()
        if not user:
            user = CustomUser.objects.create_superuser(email=login_email, password=login_password)