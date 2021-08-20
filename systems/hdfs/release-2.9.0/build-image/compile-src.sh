script="$0"
CURR_DIR="$(dirname $script)"
# hadoop is a huge project, we leave it here
#rm -rf $CURR_DIR/hadoop
SRC_LOCATION=`cat ${CURR_DIR}/../../hadoop.srclocation`
if [[ ! -e $CURR_DIR/hadoop ]]; then
    cp -r $SRC_LOCATION $CURR_DIR/
fi
cd $CURR_DIR/hadoop
git checkout release-2.9.0-RC0
#git checkout 4b8de154aa810f7e02a223393ca27235c416a352
#mvn package -Pdist -DskipTests -Dtar
mvn clean && mvn package -Pdist -DskipTests -Dtar
cd -

# current trunk is at hadoop-3.4.0-SNAPSHOT.tar.gz
cp $CURR_DIR/hadoop/hadoop-dist/target/hadoop-2.9.0.tar.gz $CURR_DIR/
