script="$0"
CURR_DIR="$(dirname $script)"
rm -rf $CURR_DIR/hive
SRC_LOCATION=`cat ${CURR_DIR}/../../hive.srclocation`
cp -r $SRC_LOCATION $CURR_DIR/
cd $CURR_DIR/hive
mvn clean package -Pdist [-DskipTests -Dmaven.javadoc.skip=true]
git checkout rel/release-3.0.0
mvn package -Pdist -DskipTests -Dtar
rm -rf $CURR_DIR/hive/.git/
cd -

cp  $CURR_DIR/hive/packaging/target/apache-hive-3.0.0-bin.tar.gz $CURR_DIR/
