#!/bin/bash

###
# mac 环境的一些命令行工具
###

function Install_vim_plugin_managers() {
	# pathogen
	mkdir -p ~/.vim/autoload ~/.vim/bundle && \
		curl -LSso ~/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim

	# vundle
	git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
}

#brew install telnet
Install_vim_plugin_managers
brew install autojump
