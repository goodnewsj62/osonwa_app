FROM python:3.8-alpine

WORKDIR /app/www

COPY ../requirements.txt /app/www

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN  pip install -r requirements.txt

COPY ../ /app/www/

