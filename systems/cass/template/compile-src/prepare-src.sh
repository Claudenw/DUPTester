# This script is used when you want to compile a branch or tag in your git repo.
# If you want to test uncommitted changes, manually prepare your src code under ./src/

script="$0"
CURR_DIR="$(dirname $script)" # this is a relative path to where you executed this script
rm -rf $CURR_DIR/src/
mkdir $CURR_DIR/src/
SRC_LOCATION=`cat ${CURR_DIR}/../../cassandra.srclocation`
cp -r $SRC_LOCATION $CURR_DIR/src/
cp $CURR_DIR/compile-src.sh $CURR_DIR/src/
cd $CURR_DIR/src/cassandra
ant clean
git checkout versionNumber
cd -
rm -rf $CURR_DIR/src/cassandra/.git/
