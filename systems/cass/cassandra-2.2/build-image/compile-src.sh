script="$0"
CURR_DIR="$(dirname $script)"
rm -rf $CURR_DIR/cassandra
SRC_LOCATION=`cat ${CURR_DIR}/../../cassandra.srclocation`
cp -r $SRC_LOCATION $CURR_DIR/
cd $CURR_DIR/cassandra
ant clean
#git checkout e889ee408bec5330c312ff6b72a81a0012fdf2a5
#git checkout bf1ea024d50dc0243bb8cec2a23b01a709b4e705
git checkout cassandra-2.1.17
ant
rm -rf $CURR_DIR/cassandra/.git/
cd -

tar -czf $CURR_DIR/cassandra.tar.gz -C $CURR_DIR cassandra
