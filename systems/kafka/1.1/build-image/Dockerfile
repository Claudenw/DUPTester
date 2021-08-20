FROM openjdk:8-jdk

# 1. General setup. 

# Use supervisor to run multiple processes, in case the target system requires
# multiple processes. 
# Remember to open port 22 for sshd.
#RUN apt-get update && apt-get install -y --allow-unauthenticated openssh-server supervisor
RUN apt-get update && apt-get install -y openssh-server supervisor vim
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD general-setup.sh /usr/local/bin/general-setup.sh
RUN sh /usr/local/bin/general-setup.sh

# 2. System setup. 

COPY kafka.tar.gz /kafka.tar.gz
ADD kafka-setup.sh /usr/local/bin/kafka-setup.sh
# This file contains relatively permanent configurations. 
RUN sh /usr/local/bin/kafka-setup.sh
ENV KAFKA_CONFIG /kafka/config
# This file contains all the runtime configurations (configurations that might
# need to be modified everytime Cassandra is run, e.g., logging level.)
ADD kafka-clusternode.sh /usr/local/bin/kafka-clusternode

# This can be overwritten in docker-compose.yaml by setting command
EXPOSE 2181 9092
CMD ["/usr/bin/supervisord"]

