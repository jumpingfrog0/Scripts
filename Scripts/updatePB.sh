#!/bin/bash

pbProjName="gamevoice-pb"
gitUrl="https://git.duowan.com/opensource/voice-business/"${pbProjName}".git"
currentProjectRootDir=$(dirname "$PWD")
originProtoPath=$currentProjectRootDir/PikoCore/PikoCore/originproto
outputProtoPath=$currentProjectRootDir/PikoCore/PikoCore/proto

mkdir -p RemotePB
echo "STEP1:创建临时目录:RemotePB"
cd RemotePB
RemotePBDir=`pwd`
echo "STEP2:git clone远程PB文件"
echo ${gitUrl}
git clone ${gitUrl}
cd ${pbProjName}

echo "STEP3:将远程PB文件拷贝到本地工程PB目录"
for proto in `find ./ -name "*.proto"`
  do
    cp $proto $originProtoPath
  done

echo "STEP4:生成PB对应的OC文件"
cd $originProtoPath
for proto in `find ./ -name "*.proto"`
  do
    protoc $proto --objc_out=$outputProtoPath --proto_path=./
  done

#if gem list xcodeproj -i > /dev/null 2>&1; then
   #ruby $currentProjectRootDir/Scripts/addPbFiles.rb
#else
   #echo "还没安装xcodeproj库"
   #echo "安装xcodeproj库可自动引入pb生成的源文件"
#fi
echo "STEP5:删除临时目录RemotePB，处理完成🍺"
rm -rf $RemotePBDir

