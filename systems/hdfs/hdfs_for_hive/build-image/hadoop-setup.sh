tar zxf /hadoop-2.9.0.tar.gz
mv /hadoop-2.9.0 /hadoop

# Don't set HADOOP_LOG_DIR and all system logs will be in /hadoop/logs/
# export HADOOP_LOG_DIR=/var/log/hdfs

# By default, hadoop uses /tmp/ to store its data, including:
# - hadoop-root-namenode.pid (.pid files)
# - hadoop-root/dfs/ (hdfs data)
# and more.
# Thus, in docker-compose.yml, we need to map
# 1) /tmp/
# 2) /hadoop/logs/
# to host directory

# change environment setup

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
#export HDFS_NAMENODE_OPTS="-XX:+UseParallelGC -Xmx512m"
export HADOOP_HEAPSIZE_MAX=512m
export HADOOP_HOME=/hadoop
export HADOOP_CONF=$HADOOP_HOME/etc/hadoop
for f in $HADOOP_HOME/contrib/capacity-scheduler/*.jar; do
  if [ "$HADOOP_CLASSPATH" ]; then
    export HADOOP_CLASSPATH=$HADOOP_CLASSPATH:$f
  else
    export HADOOP_CLASSPATH=$f
  fi
done
