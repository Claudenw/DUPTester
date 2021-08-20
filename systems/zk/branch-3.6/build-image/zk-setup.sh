tar zxf /zookeeper.tar.gz

# create necessary dirs 
mkdir -p /var/lib/zookeeper
mkdir -p /var/log/zookeeper

# create configuration file
cp /zookeeper/conf/zoo_sample.cfg /zookeeper/conf/zoo.cfg

# change environment setup
export JVMFLAGS="-Xmx512m"
export ZK_CONFIG=/zookeeper/conf

# set log directory
sed -i 's/zookeeper\.log\.dir=\./zookeeper\.log\.dir=\/var\/log\/zookeeper/' $ZK_CONFIG/log4j.properties
