FROM python:3.8-alpine

WORKDIR /app/www

ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add libc-dev linux-headers postgresql-dev gcc python3-dev musl-dev libffi-dev

RUN pip install --upgrade pip && pip3 install uwsgi

COPY ../requirements.txt /app/www

RUN  pip install -r requirements.txt

COPY ../ /app/www/

