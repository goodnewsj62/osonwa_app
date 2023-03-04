FROM python:3.8-alpine

WORKDIR /app/www

ENV PYTHONUNBUFFERED 1
COPY ../requirements.txt /app/www

RUN set -ex  && apk update \
    && apk add libc-dev linux-headers gcc python3-dev musl-dev libffi-dev \
    && && apk add --no-cache --virtual .build-deps postgresql-dev build-base \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps


ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

RUN pip install --upgrade pip && pip3 install uwsgi

COPY ../ /app/www/

EXPOSE 8000

CMD ["celery", "-A", "osonwa" ,"worker", "-l info" "-P prefork" "-Q cpu","--scheduler","django_celery_beat.schedulers:DatabaseScheduler"]