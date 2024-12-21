### DJANGO REST WITH JWT inspiration video: https://www.youtube.com/watch?v=6AEvlNgRPNc

### steps
- 1- python -m venv venv
- 2- venv\Scripts\activate
- 2.1 - python.exe -m pip install --upgrade pip
- 3- pip install django
- 4- pip install djangorestframework
- 5- pip install djangorestframework-simplejwt
- 6- django-admin startproject base .  
- 7- python manage.py startapp api   
- 8- after... we need other packages (pip install -r requirements)

### the initial migration should be execute  (python manage.py migrate)
- for each new changes in models har to be execute the makemigrations and the migrate commands...


### env example 

ENVIROMENT='development'
SECRET_KEY='5qvi$4$y16y*1q&zq=crcm6bv@qjw)*o88e7zg4xwgr1fk&dd4'
ENCRYPT_KEY = '1232145346315jlk1jklfn2lj3rlk1mflkj3löjrflm3o'
DBNAME= 'basedb'
DBUSER= 'postgres'
DBPASSWORD= 'postgres'
PGEMAIL='pgadmin4@pgadmin.org'
PGPASSWORD='root'
LOGIN_EMAIL='test@test.com'
LOGIN_PASSWORD='admin'
FHIR_NAME='hapi_demo'
FHIR_HOST='https://hapi.fhir.org/baseR4/'
FHIR_DESCR='hapi fhir demo which supports R4'
PACS_NAME='dicomserver'
PACS_HOST='www.dicomserver.co.uk'
PACS_PORT='104'




