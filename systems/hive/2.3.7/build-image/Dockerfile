FROM image_hdfs_hdfs_for_hive:latest

# 1. General setup.

# Use supervisor to run multiple processes, in case the target system requires
# multiple processes.
RUN apt-get update && apt-get install -y ssh pdsh supervisor vim rename
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD general-setup.sh /usr/local/bin/general-setup.sh
RUN sh /usr/local/bin/general-setup.sh

# using this config to omit manual confirming server's ssh key
ADD ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config
RUN chown root:root /root/.ssh/config

# 2. System setup.
COPY apache-hive-2.3.7-bin.tar.gz apache-hive-2.3.7-bin.tar.gz
RUN tar zxf /apache-hive-2.3.7-bin.tar.gz
RUN mv /apache-hive-2.3.7-bin /hive

ENV HIVE_HOME /hive
ENV PATH $HIVE_HOME/bin:$PATH
ENV HIVE_CONF /hive/conf
ENV HADOOP_HOME /hadoop
ENV HADOOP_CONF $HADOOP_HOME/etc/hadoop

RUN rename 's/\.template//' $HIVE_CONF/*

COPY hadoop-env.sh $HADOOP_CONF/
COPY core-site.xml $HADOOP_CONF/
COPY hdfs-site.xml $HADOOP_CONF/
COPY hive-env.sh $HIVE_CONF/
COPY hive-site.xml $HIVE_CONF/
COPY data_create.sh /data_create.sh
COPY remove_dbex.sh /remove_dbex.sh
COPY create_table.sql /create_table.sql
COPY read_data.sql /read_data.sql

COPY hive-startup.sh /usr/local/bin/hive-startup
RUN chmod +x /usr/local/bin/hive-startup

EXPOSE 9083 9000

EXPOSE 22

CMD ["/usr/bin/supervisord"]
