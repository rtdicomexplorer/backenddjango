#!/bin/sh
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py seed_db
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 baseproject.wsgi:application