

### steps to use the backend
- 1- python -m venv venv
- 2- venv\Scripts\activate
- 2.1 - python.exe -m pip install --upgrade pip
- 2.2 - pip install -r requirements.txt
- 2.3 - python manage.py makemigrations
- 2.4 - python manage.py migrate
- 2.5 - python manage.py seed_db
- 2.6 - python manage.py collectstatic
- 2.7 - to avoid a warning create s folder "static" on the root level




### env example 
You can use and update the .env_sample file provided


### TO DO
 Client Credentials grant  
 demo : https://django-oauth-toolkit.readthedocs.io/en/latest/tutorial/tutorial_01.html
 the front end part should be implemented as well...


 ### for the beginning
- 3- pip install django
- 4- pip install djangorestframework
- 5- pip install djangorestframework-simplejwt
- 6- django-admin startproject base .  
- 7- python manage.py startapp api   
- 8- after... we need other packages (pip install -r requirements)

### the initial migration should be execute  (python manage.py migrate)
- for each new changes in models har to be execute the makemigrations and the migrate commands...

### DJANGO REST WITH JWT inspiration video: https://www.youtube.com/watch?v=6AEvlNgRPNc