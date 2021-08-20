#!/usr/bin/env bash

# Get running container's IP
IP=`hostname --ip-address | cut -f 1 -d ' '`

echo "Starting HBase on $IP..."

#exec $HBASE_HOME/bin/start-hbase.sh
