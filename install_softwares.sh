#!/bin/bash

###
# 一些工具软件的一键安装脚本
###

function install() {
	is_installed="$(brew cask list | grep -E -i $1)"
	if [[ ! -z "${is_installed}" ]]; then
		echo "Info: '$1' have been installed."
	else
		brew cask install $1	
	fi
}

installed_list="$(brew cask list)"
echo "${installed_list}"

install shiftit
#install iterm2
#install macdown
#install visual-studio-code

# 需要破解版
#install dash







#brew cask install shiftit
#brew cask install iterm2
#brew cask install macdown
#brew cask install visual-studio-code
#brew cask install dash

# alfred need to hack
# brew cask install alfred

#is_installed=`brew cask install sourcetree | grep -q -E -i "error"`
#if [[ ! -z ${is_installed} ]]; then
#	echo "Error: Install 'sourcetree' failed."
#fi
