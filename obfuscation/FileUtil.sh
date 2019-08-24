#!/bin/bash

# 循环检测输入的文件夹
checkInputDestDirRecursive() {
	echo -n "请输入目录: "
	read path
	if [[ -d $path ]]; then
		CheckInputDestDirRecursiveReturnValue=$path
	else
		echo -n "输入的目录无效，"
		checkInputDestDirRecursive
	fi
}

# 检测文件夹存在的方法，结果保存在全局变量`CheckInputDestDirRecursiveReturnValue`中
# 参数一：检测的文件夹路径
# 参数二：提示消息字符串
# 使用方式如下，去掉注释
# # 导入工具脚本
# . ./FileUtil.sh
# # 检测class_search_dir
# checkDirCore $class_search_dir "指定类的查找目录不存在"
# class_search_dir=${CheckInputDestDirRecursiveReturnValue}
checkDirCore() {
	to_process_dir=$1
	message=$2
	# 需处理源码目录检查
	if [[ -d $to_process_dir ]]; then
		echo "目录存在 $to_process_dir"
		CheckInputDestDirRecursiveReturnValue=$to_process_dir
		return 1
	else
		echo "${message} ${to_process_dir}"
		checkInputDestDirRecursive ${to_process_dir}
	fi
}

# 检测文件是否存在，不存在则创建
checkOrCreateFile() {
	file=$1
	if [[ -f $file ]]; then
		echo "检测到文件存在 $file"
	else
		echo "创建文件 $file"
		touch $file
	fi
}

####
# 以下是新方法, 所有脚本完成以后，删除上的旧方法
####

# 检测文件是否存在，不存在则创建
function check_or_create_file() {
	file=$1
	if [[ -f $file ]]; then
		echo "检测到文件存在: $file"
	else
		echo "创建文件: $file"
		touch $file
	fi
}

function check_exist_file() {
	file=$1
	if [[ -f $file ]]; then
		echo "检测到文件存在: $file"
	else
		echo "文件不存在: $file"
		exit 1
	fi
}

function check_file_exists() {
	file=$1
	if [[ -f $file ]]; then
		return 1
	else
		return 0
	fi
}

function check_file_exists_with_msg() {
	file=$1
	msg1=$2
	msg2=$3
	if [[ -f $file ]]; then
		echo "${msg1} ${file}"
		return 1
	else
		echo "${msg2} ${file}"
		return 0
	fi	
}

function check_file_exists_with_error_msg() {
	file=$1
	msg1=$2
	if [[ -f $file ]]; then
		return 1
	else
		echo "${msg1} ${file}"
		exit 1
	fi		
}