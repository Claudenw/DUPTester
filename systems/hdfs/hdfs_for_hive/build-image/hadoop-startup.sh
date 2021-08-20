#!/usr/bin/env bash

# Get running container's IP
IP=`hostname --ip-address | cut -f 1 -d ' '`

# single node
sed -i -e "s/HOSTNAME/localhost/" $HADOOP_CONF/core-site.xml

echo "Starting Cassandra on $IP... Config dir $HADOOP_CONF"

service sshd start

# config this node depending on what service it needs to run
# - hdfs master node
# - hdfs data node
# - yarn resource manager
# - yarn node manager
# - mapreduce history server

# only format namenode if this dir doesn't exist or has nothing
namedir=/tmp/hadoop-root/dfs/name

if [[ ! -e $namedir ]]; then
    cho "No name node. Formatting namenode name directory: $namedir"
    $HADOOP_HOME/bin/hdfs namenode -format
elif [[ ! -d $namedir ]]; then
    cho "NameNode dir is not a directory. Formatting namenode name directory: $namedir"
    $HADOOP_HOME/bin/hdfs namenode -format
elif [ "`ls -A $namedir`" == "" ]; then
  echo "NameNode not formatted. Formatting namenode name directory: $namedir"
  $HADOOP_HOME/bin/hdfs namenode -format
fi

$HADOOP_HOME/sbin/start-dfs.sh -upgrade
$HADOOP_HOME/sbin/start-yarn.sh
$HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
