script="$0"
CURR_DIR="$(dirname $script)"

docker build -t cass-image-3.10 $CURR_DIR
