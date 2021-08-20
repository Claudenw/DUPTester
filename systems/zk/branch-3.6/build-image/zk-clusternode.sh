#!/usr/bin/env bash

# Get running container's IP
IP=`hostname --ip-address | cut -f 1 -d ' '`

# Change the logging level accordingly
if [ -z "$CASSANDRA_LOGGING_LEVEL" ]; then
        echo "No log level specified, preserving default INFO" 
else
        sed -i -e "s/^log4j.rootLogger=.*/log4j.rootLogger=$CASSANDRA_LOGGING_LEVEL,stdout,R/" $ZK_CONFIG/log4j.properties >>  /tmp.log 2>&1 
fi

# Generate the config only if it doesn't exist
if [[ -f "/zookeeper/conf/zoo.cfg" ]]; then
    CONFIG="/zookeeper/conf/zoo.cfg"
    if grep "server.1=" $CONFIG > /dev/null
    then
        echo "Server exists"
    else
        #echo "Server does not exist"
        if [[ -z $ZOO_SERVERS ]]; then
            ZOO_SERVERS="server.1=localhost:2888:3888"
        fi
	#echo "autopurge.snapRetainCount = 10"  >> "$CONFIG"
	#echo "autopurge.purgeInterval = 2"  >> "$CONFIG"
        echo "snapshot.trust.empty=true" >> "$CONFIG"
        for server in $ZOO_SERVERS; do
            echo "$server" >> "$CONFIG"
        done
    fi
fi

# Write myid only if it doesn't exist
if [[ ! -f "/tmp/zookeeper/myid" ]]; then
    echo "${ZOO_MY_ID:-1}" > /tmp/zookeeper/myid
fi

#export ZOOPIDFILE=/tmp/zookeeper/zookeeper_server.pid

echo "Starting ZooKeeper on $IP..."

exec /zookeeper/bin/zkServer.sh start-foreground
