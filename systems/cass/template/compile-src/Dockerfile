#FROM openjdk:6
FROM openjdk:7

RUN apt-get update && apt-get install -y supervisor vim ant
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /compile-src/

ADD compile-src.sh /usr/local/bin/compile-src.sh

CMD ["/usr/bin/supervisord"]
