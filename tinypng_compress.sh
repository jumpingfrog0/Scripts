#!/bin/bash

###
# 右键快捷键用tinypng压缩图片
# 
# 操作步骤：
# 1. 打开 `Automator.app`
# 2. 选择 `实用工具` --> `运行Shell脚本` --> 拖动到右边新建一个脚本
# 3. 传递输入 选择 `作为自变量`
# 4. 工作流程收到当前选择工具应用的文件类型（如：图像文件）
# 5. 粘贴脚本，保存，命名脚本工具（如tinypng_compress)
# 6. 右键 --> 服务 --> tinypng_compress
# 7. 脚本运行，在右上角的工具栏中会有一个齿轮⚙在转，脚本运行完成后齿轮消失
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