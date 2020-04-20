#!/bin/bash

###
# 右键快捷键用tinypng压缩图片
###

# input your tiny png API key
tinyPNGKey=<YOUR_TINYPNG_API_KEY>

compress(){
    fileName=$1
    echo "origin file name : $fileName"
    compressUrl=$(/usr/bin/curl --user api:$tinyPNGKey --data-binary @$fileName --silent -i https://api.tinify.com/shrink | grep location: | awk '{print $2}' | tr -d '\r')

    if test -z "$compressUrl"
    then
        echo "compress url is empty"
    else
        echo "compress url: $compressUrl"
        dirName=$(dirname $fileName)
        baseName=$(basename $fileName)
        newFileName="$dirName/compress-$baseName"
        curl -o $newFileName $compressUrl
    fi
}

for param in "$@"; do
    compress $param
done