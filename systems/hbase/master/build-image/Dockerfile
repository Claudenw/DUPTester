FROM openjdk:8-jdk

# 1. General setup.

# Use supervisor to run multiple processes, in case the target system requires
# multiple processes.
RUN apt-get update && apt-get install -y ssh pdsh supervisor vim
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD general-setup.sh /usr/local/bin/general-setup.sh
RUN sh /usr/local/bin/general-setup.sh

# using this config to omit manual confirming server's ssh key
ADD ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config
RUN chown root:root /root/.ssh/config

# 2. System setup. 

COPY hbase-3.0.0-SNAPSHOT-bin.tar.gz /hbase-3.0.0-SNAPSHOT-bin.tar.gz
RUN tar zxf /hbase-3.0.0-SNAPSHOT-bin.tar.gz
RUN mv /hbase-3.0.0-SNAPSHOT /hbase

# JAVA_HOME is in a different place in the base container image
#ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV JAVA_HOME /usr/local/openjdk-8
RUN echo "export JAVA_HOME=/usr/local/openjdk-8" >> /hbase/conf/hbase-env.sh
ENV HBASE_HOME /hbase

ADD hbase-site.xml $HBASE_HOME/conf/hbase-site.xml
COPY regionservers $HBASE_HOME/conf/regionservers

RUN mkdir /var/lib/hbase
RUN mkdir /var/lib/zookeeper

# 3. startup script
ADD hbase-startup.sh /usr/local/bin/hbase-startup

EXPOSE 8020 2181 8080 8085 9090 9095 16000 16010 16030 16201 16301 22

CMD ["/usr/bin/supervisord"]
