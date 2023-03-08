FROM python:3.8-alpine

WORKDIR /app/www

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /app/www

RUN set -ex  && apk update \
    && apk add linux-headers gcc python3-dev musl-dev libffi-dev \
    && apk add postgresql-dev 

RUN pip install --upgrade pip && pip install -r requirements.txt    

RUN  pip3 install uwsgi -I --no-cache-dir

COPY ./ /app/www/

EXPOSE 8000

CMD ["uwsgi",  "--ini", "osonwa.ini"]