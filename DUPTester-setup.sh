script="$0"
CURR_DIR="$(dirname $(readlink -f $script))"

sudo apt-get update
sudo apt-get install docker-io 
sudo apt-get install python3-docker 
sudo apt-get install docker-compose 
sudo apt-get install docker.io
sudo chmod 666 /var/run/docker.sock
sudo apt-get install ant maven
sudo apt-get install python3-pip
pip3 install docker 
pip3 install numpy 
pip3 install pandas
pip3 install astunparse 
pip3 install cassandra-driver 
pip3 install javalang

APP_DIR="$CURR_DIR/applications"
SYS_DIR="$CURR_DIR/systems"
mkdir $APP_DIR
cd $APP_DIR

git clone https://github.com/apache/cassandra
git clone https://github.com/apache/hbase
git clone https://github.com/apache/hive
git clone https://github.com/apache/kafka
git clone https://github.com/apache/zookeeper

cd ..
echo $APP_DIR/cassandra > $SYS_DIR/cass/cassandra.srclocation
echo $APP_DIR/hbase > $SYS_DIR/hbase/hbase.srclocation
echo $APP_DIR/hive > $SYS_DIR/hive/hive.srclocation
echo $APP_DIR/kafka > $SYS_DIR/kafka/kafka.srclocation
echo $APP_DIR/zookeeper > $SYS_DIR/zk/zk.srclocation

