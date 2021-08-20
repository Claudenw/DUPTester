script="$0"
CURR_DIR="$(dirname $script)"
rm -rf $CURR_DIR/cassandra
SRC_LOCATION=`cat ${CURR_DIR}/../../cassandra.srclocation`
cp -r $SRC_LOCATION $CURR_DIR/
cd $CURR_DIR/cassandra
ant clean
git checkout 6137b381d2d619ff094395ea32cc4730b9969682
ant
rm -rf $CURR_DIR/cassandra/.git/
cd -

tar -czf $CURR_DIR/cassandra.tar.gz -C $CURR_DIR cassandra
