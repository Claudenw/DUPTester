#!/bin/bash

source $(dirname $0)/config.lib
source $(dirname $0)/../scripts/utils.lib

echo WORKING_DIR=${WORKING_DIR}
echo BRANCH=${BRANCH}
echo docker_pfx=${docker_pfx}
#  branch contains systems subdirectory

if [ `grep -c /systems/${BRANCH}/git ../../.gitignore` -eq 0 ]
then
  echo /systems/${BRANCH}/\*\*/${name} >> ../../.gitignore
  echo /systems/${BRANCH}/git >> ../../.gitignore
fi

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
rsync -v ${WORKING_DIR}/../scripts/templates/* ${WORKING_DIR}/${BRANCH}
chmod ugo+x ${WORKING_DIR}/${BRANCH}/compile-src
chmod ugo+x ${WORKING_DIR}/${BRANCH}/build-docker-image

${WORKING_DIR}/${BRANCH}/compile-src
if [ $? -ne 0 ]
then
	echo "compile-src failed"
	exit 1
fi
${WORKING_DIR}/${BRANCH}/build-docker-image
if [ $? -ne 0 ]
then
	echo "build-docker-image failed"
	exit 1
fi


