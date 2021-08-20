script="$0"
CURR_DIR="$(dirname $script)"
rm -rf $CURR_DIR/zookeeper
SRC_LOCATION=`cat ${CURR_DIR}/../../zk.srclocation`
cp -r $SRC_LOCATION $CURR_DIR/
cd $CURR_DIR/zookeeper
mvn clean 
git checkout branch-3.6
mvn install -DskipTests
rm -rf ./.git/
cd ..

tar -czf $CURR_DIR/zookeeper.tar.gz -C $CURR_DIR zookeeper
