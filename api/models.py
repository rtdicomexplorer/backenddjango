from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.conf import settings

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('image', "default/user.png")
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    username = None
    image = models.ImageField(upload_to = settings.AVATARS_URL, null=True, blank=True)
    email = models.EmailField(blank=True, default='', unique=True)
    name = models.CharField(max_length=255, blank=True, default='')

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []   

    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name or self.email
    def __str__(self):
        return self.email or self.name
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class FhirServer(models.Model):
    name = models.CharField(max_length=255,blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    host = models.CharField(max_length=255, blank=False, null=False)
    image = models.ImageField(upload_to='server/', blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
            verbose_name_plural = "FhirServers"
            unique_together = ('name',)


    @property
    def get_url(self):
        return self.host
    
    def __str__(self):
        return self.name

class DicomServer(models.Model):
    aetitle = models.CharField(max_length=16, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    host = models.CharField(max_length=255, blank=False, null=False)
    port = models.PositiveIntegerField(null=True)
    image = models.ImageField(upload_to='server/', blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
            verbose_name_plural = "DicomServers"
            unique_together = ('aetitle',)

    @property
    def get_url(self):
        return self.host+':'+self.port
    
    def __str__(self):
        return self.aetitle
