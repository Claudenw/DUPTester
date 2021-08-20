tar zxf /kafka.tar.gz

# create necessary dirs (some version of cassandra cannot create these)
mkdir -p /var/log/kafka
mkdir -p /var/lib/kafka

# change environment setup

# Note that runtime setup such as SEED is set in 
#sed -i 's/Xss128k/Xss256k/' /cassandra/conf/cassandra-env.sh

# config on-disk data locations

export KAFKA_HOME=/kafka/
