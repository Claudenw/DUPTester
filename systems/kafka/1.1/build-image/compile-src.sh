script="$0"
CURR_DIR="$(dirname $script)"
rm -rf $CURR_DIR/kafka
SRC_LOCATION=`cat ${CURR_DIR}/../../kafka.srclocation`
cp -r $SRC_LOCATION $CURR_DIR/
cd $CURR_DIR/kafka
./gradlew clean
git checkout 1.1
./gradlew jar
rm -rf $CURR_DIR/kafka/.git/
cd -

tar -czf $CURR_DIR/kafka.tar.gz -C $CURR_DIR kafka
