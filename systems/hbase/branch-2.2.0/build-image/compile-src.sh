script="$0"
CURR_DIR="$(dirname $script)"
# hbase is a huge project, we leave it here
#rm -rf $CURR_DIR/hbase
SRC_LOCATION=`cat ${CURR_DIR}/../../hbase.srclocation`
if [[ ! -e $CURR_DIR/hbase ]]; then
    cp -r $SRC_LOCATION $CURR_DIR/
fi
cd $CURR_DIR/hbase
git checkout refs/tags/rel/2.2.0
mvn -DskipTests clean install && mvn -DskipTests package assembly:single
cd -

# current master is at hbase-3.0.0-SNAPSHOT-bin.tar.gz
cp $CURR_DIR/hbase/hbase-assembly/target/hbase-2.2.0-bin.tar.gz $CURR_DIR/
