#!/bin/bash

############## 工具类方法
function printHighlightMessage {
	#mark: echo 颜色选项 http://www.jb51.net/article/43968.htm
	echo -e "\033[31m $1 \033[0m"
}

# 检测是否安装gun sed，mac 内置的sed会有些问题，所以需要安装gun sed
gunSedInstallCheck() {
	# 检查是否安装gunsed
	# mac安装gunSed  http://blog.csdn.net/sun_wangdong/article/details/71078083
	which_sed=`which sed`
	echo $which_sed
	echo "testresult = $(expr "$which_sed" : '.*/gnu-sed/')"
	which_sed=`ls -al ${which_sed}`
	echo $which_sed
	echo "testresult = $(expr "$which_sed" : '.*/gnu-sed/')"
	if [[ $(expr "$which_sed" : '.*/gnu-sed/') -gt 0 ]]; then
		echo "检测到使用gun sed"
	else
		if [ ! `which brew` ]
		then
			echo 'Homebrew not found. Trying to install...'
	                    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" \
				|| exit 1
		fi
		echo 'Trying to install gun sed...'
		brew install gnu-sed
		# 设置局部环境变量
		# echo "set PATH...."
		# source ./set-gun-sed-path.sh
		# echo "set PATH done"

		echo "请手动执行命令,然后重新执行"
		# command="PATH=\"/usr/local/Cellar/gnu-sed/4.5/bin:\$PATH\""
		export PATH="/usr/local/opt/gnu-sed/libexec/gnubin:$PATH"
		printHighlightMessage $command
		echo ""
		exit 1
	fi
}

md5SumInstalCheck() {
	if [ ! `which md5Sum` ]
		then
		# https://blog.csdn.net/cup_chenyubo/article/details/52982986
		brew install md5sha1sum || exit 1
	fi
}

# 检测是否安装 home brew
function check_install_brew() {
	if [ ! `which brew` ]
	then
		echo 'Homebrew not found. Trying to install...'
					ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" \
			|| exit 1
	fi
}

# 检测是否安装jq
function check_install_jq() {
	which_jq=`which jq`
	echo $which_jq
	echo "testresult = $(expr "$which_sed" : '.*/jq')"
	if [[ $(expr "$which_jq" : '.*/jq') -gt 0 ]]; then
		echo "检测到已经安装jq"
	else
		check_install_brew
		echo "Trying to install jq..."
		brew install jq || exit 1	
		echo "Install jq Successfully."
		printHighlightMessage "Please retry to run scrips."
	fi
}


