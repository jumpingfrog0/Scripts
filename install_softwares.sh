#!/bin/bash

###
# 一些工具软件的一键安装脚本
###

brew cask install shiftit
brew cask install alfred
brew cask install iterm2
brew cask install macdown
brew cask install visual-studio-code

is_installed=`brew cask install sourcetree | grep -q -E -i "error"`
if [[ ! -e ${is_installed} ]]; then
	echo "Error: Install 'sourcetree' failed."
fi
