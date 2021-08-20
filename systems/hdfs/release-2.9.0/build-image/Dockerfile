FROM openjdk:8-jdk

# 1. General setup.

# Use supervisor to run multiple processes, in case the target system requires
# multiple processes.
# Remember to open port 22 for sshd.
RUN apt-get update && apt-get install -y ssh pdsh supervisor vim
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD general-setup.sh /usr/local/bin/general-setup.sh
RUN sh /usr/local/bin/general-setup.sh

# 2. System setup.

COPY hadoop-2.9.0.tar.gz /hadoop-2.9.0.tar.gz

#ENV HADOOP_HOME /hadoop
#ENV HADOOP_CONF $HADOOP_HOME/etc/hadoop

ADD hadoop-setup.sh /usr/local/bin/hadoop-setup.sh
RUN sh /usr/local/bin/hadoop-setup.sh

# JAVA_HOME is in a different place in the base container image
#ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV JAVA_HOME /usr/local/openjdk-8
#ENV HDFS_NAMENODE_OPTS "-XX:+UseParallelGC -Xmx512m"
ENV HADOOP_LOG_DIR /var/log/hdfs
ENV HADOOP_HEAPSIZE_MAX 512m
ENV HADOOP_HOME /hadoop
ENV HADOOP_CONF $HADOOP_HOME/etc/hadoop
#ENV USER=root

ENV HDFS_NAMENODE_USER="root"
ENV HDFS_DATANODE_USER="root"
ENV HDFS_SECONDARYNAMENODE_USER="root"
ENV YARN_RESOURCEMANAGER_USER="root"
ENV YARN_NODEMANAGER_USER="root"

ADD core-site.xml $HADOOP_CONF/core-site.xml
ADD hdfs-site.xml $HADOOP_CONF/hdfs-site.xml
ADD mapred-site.xml $HADOOP_CONF/mapred-site.xml
ADD yarn-site.xml $HADOOP_CONF/yarn-site.xml

# JAVA_HOME has to be set in hadoop-env.sh
RUN sed -i 's/^\$HADOOP_HOME\/contrib\/capacity-scheduler/\$HADOOP_HOME\/share\/hadoop\/tools\/lib/' $HADOOP_CONF/hadoop-env.sh
RUN sed -i 's/^export JAVA_HOME=${JAVA_HOME}/export JAVA_HOME=\/usr\/local\/openjdk-8/' $HADOOP_CONF/hadoop-env.sh
RUN sed -i 's/^# export HADOOP_HOME=/export HADOOP_HOME=\/hadoop/' $HADOOP_CONF/hadoop-env.sh
RUN sed -i 's/^# export HADOOP_CONF_DIR=/export HADOOP_CONF_DIR=/' $HADOOP_CONF/hadoop-env.sh

# PDSH doesn't work without telling it to use ssh (it'll use rsh which doesn't work)
RUN echo "export PDSH_RCMD_TYPE=ssh" >> $HADOOP_CONF/hadoop-env.sh
RUN echo "export HADOOP_CLASSPATH=$HADOOP_CLASSPATH:$HADOOP_HOME/share/hadoop/tools/lib/*" >> $HADOOP_CONF/hadoop-env.sh

# using this config to omit manual confirming server's ssh key
ADD ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config
RUN chown root:root /root/.ssh/config

ADD hadoop-startup.sh /usr/local/bin/hadoop-startup

# Hdfs ports
EXPOSE 50010 50020 50070 50075 50090
# Mapred ports
EXPOSE 19888
#Yarn ports
EXPOSE 8030 8031 8032 8033 8040 8042 8088
#Other ports
EXPOSE 22

CMD ["/usr/bin/supervisord"]
