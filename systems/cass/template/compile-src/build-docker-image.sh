script="$0"
CURR_DIR="$(dirname $script)"

docker build -t cass-compile-image $CURR_DIR

