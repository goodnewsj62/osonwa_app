FROM python:apline

WORKDIR /app/www

RUN pip install celery

RUN pip install Redis


