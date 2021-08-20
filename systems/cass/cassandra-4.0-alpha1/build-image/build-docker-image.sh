script="$0"
CURR_DIR="$(dirname $script)"

docker build -t cass-image-4.0-alpha1 $CURR_DIR
