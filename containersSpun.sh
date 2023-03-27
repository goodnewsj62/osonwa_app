#! /usr/bin/bash

sudo docker build  -t osonwa:v0 -f ./prod.dockerfile .
sudo docker build  -t cpucelery:v0 -f ./cpucelery.dockerfile .
sudo docker build --no-cache -t iocelery:v0 -f ./iocelery.dockerfile .


sudo docker run -d --name iocelery_beat -v /var/log/osonwa:/app/www/logs --env-file .env --network=host iocelery:v0 sh -c "celery -A osonwa beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
sudo docker run -d --name iocelery_worker -v /var/log/osonwa:/app/www/logs --env-file .env --network=host iocelery:v0 sh -c "celery -A osonwa worker -l info -P gevent -Q greenqueue -c 100"

sudo docker run -d --name cpucelery_beat -v /var/log/osonwa:/app/www/logs --env-file .env --network=host cpucelery:v0 sh -c "celery -A osonwa beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
sudo docker run -d --name cpucelery_worker -v /var/log/osonwa:/app/www/logs --env-file .env --network=host cpucelery:v0 sh -c "celery -A osonwa worker -l info -P prefork -Q cpu"


sudo docker conatiner prune 
sudo docker container stop iocelery_worker iocelery_beat cpucelery_worker cpucelery_beat osonwa_app
sudo docker container rm iocelery_worker iocelery_beat cpucelery_worker cpucelery_beat osonwa_app

sudo docker run -d --name osonwa_app --network=host --env-file .env -v ./media:/app/www/media -v /var/log/osonwa:/app/www/logs -v ./static:/app/www/static osonwa:v0

sudo docker run -d --network=host --env-file .env osonwa:v0 sh -c "python manage.py makemigrations && python manage.py migrate"