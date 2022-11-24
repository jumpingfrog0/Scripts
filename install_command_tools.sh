#!/bin/bash

###
# mac 环境的一些命令行工具
###

function install_zsh() {
    if [ -d ~/.oh-my-zsh ]; then
        echo "zsh is installed."
    else
        echo "Trying to install zsh..."
        # oh-my-zsh
        # brew install zsh
        # $(brew --prefix)/bin/zsh
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
    fi
    
    brew install zsh-syntax-highlighting
}

function install_homebrew() {
    if [ ! `which brew` ]
    then
	echo 'Homebrew not found. Trying to install Homebrew...'
    	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi
}

function install_homebrew_cask() {
    result=$('which brew cask')
    echo $result
    if [[ "$result" != ""  ]]
    then
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
    [[ -s /opt/homebrew/etc/autojump.sh ]] && . /opt/homebrew/etc/autojump.sh" >> ~/.zshrc
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

function install_node() {
    # node
    echo "Trying to install node..."
    brew install node
}

function install_ss_manager() {
    # shadowsocks-manager
    echo "Trying to install shadowsocks-manager..."
	npm i -g shadowsocks-manager
}

function install_telnet() {
    echo "Trying to install telnet..."
	brew install telnet
}

# required
install_zsh
#install_homebrew
#install_homebrew_cask
install_vim_plugin_managers
install_autojump
install_tree
install_iStats
install_node
install_telnet

# option
#install_gnu_sed
#install_ss_manager
