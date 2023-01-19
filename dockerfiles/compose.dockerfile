FROM python:3.8-alpine

WORKDIR /app/www

ENV PYTHONUNBUFFERED 1

RUN apk add libc-dev linux-headers postgresql-dev gcc python3-dev musl-dev libffi-dev

COPY ../requirements.txt /app/www

RUN  pip install -r requirements.txt

COPY ../ /app/www/

