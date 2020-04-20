#!/bin/bash

###
# mac 环境的一些命令行工具
###

function install_homebrew() {
    if [ ! `which brew` ]
    then
	echo 'Homebrew not found. Trying to install Homebrew...'
    	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	brew tap caskroom/cask
    fi
}

function install_vim_plugin_managers() {
	echo "Trying to install pathogen..."
	# pathogen
	mkdir -p ~/.vim/autoload ~/.vim/bundle && \
		curl -LSso ~/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim

	# vundle
	echo "Trying to install vundle..."	
	git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
}

function install_autojump() {
    echo "Trying to install autojump..."
    brew install autojump
    echo "\n# autojump configuration\n \
    [[ -s `brew --prefix`/etc/autojump.sh ]] && . `brew --prefix`/etc/autojump.sh" >> ~/.zshrc
    source ~/.zshrc
}

function install_tree() {
    # tree
    echo "Trying to install tree..."
    brew install tree
}

function install_iStats() {
    # tree
    echo "Trying to install iStats..."
    gem install iStats
}

function install_gnu_sed() {
	brew install gnu-sed
	sed -i '$a\ # gnu-sed \
 export PATH=\"/usr/local/opt/gnu-sed/libexec/gnubin:$PATH\"' ~/.zshrc
}

#install_homebrew
#brew install telnet
#install_vim_plugin_managers
#install_autojump
#install_tree
#install_iStats
install_gnu_sed