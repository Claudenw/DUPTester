#!/bin/bash

source $(dirname $0)/utils.lib

if [ -z "$1" ]
then
  echo "Version must be specified on the command line"
  exit 1
fi

export BRANCH=$1

if [ ${BRANCH} == "template" ]
then
  echo "Version may not be 'template'"
  exit 1
fi


if [ ! -d ${WORKING_DIR}/${BRANCH}/build-image ]
then
  mkdir -p ${WORKING_DIR}/${BRANCH}/build-image
fi

rsync -v ${WORKING_DIR}/template/build-image/* ${WORKING_DIR}/${BRANCH}/build-image
mv ${WORKING_DIR}/${BRANCH}/build-image/compile-src ${WORKING_DIR}/${BRANCH}
chmod ugo+x ${WORKING_DIR}/${BRANCH}/compile-src
mv ${WORKING_DIR}/${BRANCH}/build-image/build-docker-image  ${WORKING_DIR}/${BRANCH}
chmod ugo+x ${WORKING_DIR}/${BRANCH}/build-docker-image

${WORKING_DIR}/${BRANCH}/compile-src
${WORKING_DIR}/${BRANCH}/build-docker-image


