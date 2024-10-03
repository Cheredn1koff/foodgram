#!/bin/sh

export DJANGO_SETTINGS_MODULE=foodgram.settings

python manage.py migrate --noinput

python manage.py collectstatic --noinput

python manage.py load_ingredients

gunicorn --bind 0:8080 foodgram.wsgi:application