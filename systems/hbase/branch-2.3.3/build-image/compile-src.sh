script="$0"
CURR_DIR="$(dirname $script)"
# hbase is a huge project, we leave it here
rm -rf $CURR_DIR/hbase
SRC_LOCATION=`cat ${CURR_DIR}/../../hbase.srclocation`
if [[ ! -e $CURR_DIR/hbase ]]; then
    cp -r $SRC_LOCATION $CURR_DIR/
fi
cd $CURR_DIR/hbase
git checkout 7c4c3d06853c0317a22bef6da7081dbb7c102f56
#mvn install -DskipTests
mvn -DskipTests install && mvn -DskipTests package assembly:single
cd -

# current master is at hbase-3.0.0-SNAPSHOT-bin.tar.gz
cp $CURR_DIR/hbase/hbase-assembly/target/hbase-2.3.3-SNAPSHOT-bin.tar.gz $CURR_DIR/
