FROM redis 


RUN mkdir -p /var/log/redis && cd /var/log/redis && touch redis-server.log
RUN chmod a+w /var/log/redis/redis-server.log

COPY ./redis.conf /usr/local/etc/redis/redis.conf

CMD [  "redis-server", "/usr/local/etc/redis/redis.conf" ]