script="$0"
CURR_DIR="$(dirname $(readlink -f $script))"

curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs migrate import --include="*.tar.gz"
git add .gitattributes 
sudo apt-get update
sudo apt-get install docker-io openjdk-8-jdk python3-docker docker-compose
sudo chmod 666 /var/run/docker.sock
sudo apt-get install ant maven
sudo apt-get install python3-pip
pip3 install docker numpy pandas
pip3 install astunparse cassandra-driver javalang

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

