#!/bin/bash
export HADOOP_USER_NAME=hdfs
cd $HIVE_HOME/bin
./hiveserver2 --hiveconf hive.server2.enable.doAs=false &
./hive --service hiveserver2 &
