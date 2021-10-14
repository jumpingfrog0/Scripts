#!/bin/bash
#
# 日志打印工具脚本
#

function warning() {
	echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: \033[32m $1 \033[0m"
}

function err() {
	echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: \033[31m $1 \033[0m"
}

function info() {
	echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: \033[32m $1 \033[0m"
}

function print_highlight_message() {
	#mark: echo 颜色选项 http://www.jb51.net/article/43968.htm
	echo -e "\033[31m $1 \033[0m"
}

function print_info() {
	echo -e "\033[32m $1 \033[0m"
}

function print_tip() {
	echo -e "\033[33m $1 \033[0m"
}