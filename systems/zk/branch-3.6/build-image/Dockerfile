FROM openjdk:8-jdk

# 1. General setup. 

# Use supervisor to run multiple processes, in case the target system requires
# multiple processes. 
# Remember to open port 22 for sshd.
#RUN apt-get update && apt-get install -y --allow-unauthenticated openssh-server supervisor
#RUN apt-get update && apt-get install -y openssh-server supervisor
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
#ADD general-setup.sh /usr/local/bin/general-setup.sh
#RUN sh /usr/local/bin/general-setup.sh

RUN apt-get update && apt-get install -y supervisor vim
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 2. System setup. 

COPY zookeeper.tar.gz /zookeeper.tar.gz
ADD zk-setup.sh /usr/local/bin/zk-setup.sh
# This file contains relatively permanent configurations. 
RUN sh /usr/local/bin/zk-setup.sh
# ENV ZK_CONFIG /zookeeper/conf
# This file contains all the runtime configurations (configurations that might
# need to be modified everytime Cassandra is run, e.g., logging level.)
ADD zk-clusternode.sh /usr/local/bin/zk-clusternode

# This can be overwritten in docker-compose.yaml by setting command
EXPOSE 2181 2888 3888 8080
CMD ["/usr/bin/supervisord"]
