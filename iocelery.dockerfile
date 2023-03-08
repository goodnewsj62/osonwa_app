FROM python:3.8-alpine

WORKDIR /app/www

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /app/www

RUN set -ex  && apk update \
    && apk add linux-headers gcc python3-dev musl-dev libffi-dev \
    && apk add postgresql-dev 

RUN pip install --upgrade pip && pip install -r requirements.txt    

RUN  pip3 install uwsgi -I --no-cache-dir

RUN adduser -D -u 1000 -Hs /bin/bash celery

COPY ./ /app/www/

RUN chown -R celery:celery /app/www

ENV C_FORCE_ROOT=false

EXPOSE 9000

CMD ["celery","-A", "osonwa", "beat","-l","info", "-P","gevent", "-Q","greenqueue" ,"-c","100", "--scheduler","django_celery_beat.schedulers:DatabaseScheduler"]