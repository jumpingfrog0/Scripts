#!/bin/bash

###
# 一些工具软件的一键安装脚本
###

function install() {
	is_installed="$(brew list cask | grep -E -i $1)"
	if [[ ! -z "${is_installed}" ]]; then
		echo "Info: '$1' have been installed."
	else
		echo "Installing $1..."
		brew install --cask $1
	fi
}

installed_list="$(brew list --cask)"
echo "${installed_list}"

install shiftit
install iterm2
install sourcetree
#install postman
#install visual-studio-code

# 需要破解版
#install dash

# alfred need to hack
#brew install alfred --cask

#is_installed=`brew cask install sourcetree | grep -q -E -i "error"`
#if [[ ! -z ${is_installed} ]]; then
#	echo "Error: Install 'sourcetree' failed."
#fi
