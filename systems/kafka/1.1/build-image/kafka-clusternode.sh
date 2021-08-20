#!/usr/bin/env bash

# Get running container's IP
IP=`hostname --ip-address | cut -f 1 -d ' '`

# Change the logging level accordingly

# Generate the config only if it doesn't exist

# Write myid only if it doesn't exist

echo "Starting Kafka on $IP..."

cd /kafka/

nohup bin/zookeeper-server-start.sh config/zookeeper.properties &
exec bin/kafka-server-start.sh config/server.properties 
