#!/bin/bash

targetDir="${PROJECT_DIR}/.git/hooks"
if [ ! -d "${targetDir}" ];then
  mkdir ${targetDir}
fi
cp ${PROJECT_DIR}/Scripts/pre-push ${targetDir}/pre-push
exit 0

