#!/bin/bash

###
# mac 环境的一些命令行工具
###

############################   Functions   ###############################

function install_zsh() {
    if [ -d ~/.oh-my-zsh ]; then
        echo "zsh is installed."
    else
        echo "Trying to install zsh..."
        # oh-my-zsh
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
    fi
    
    brew install zsh-syntax-highlighting
}

function init_zsh() {
    brew install zsh-syntax-highlighting
}

function install_homebrew() {
    if [ ! `which brew` ]
    then
	echo 'Homebrew not found. Trying to install Homebrew...'
    	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    	echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    	eval "$(/opt/homebrew/bin/brew shellenv)"
    	source ~/.zshrc
    fi
}

function init_homebrew() {
    if [ ! `brew list --cask` ]
    then
	brew install --cask
    	#brew tap caskroom/cask
    fi
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

##########################################################################

############################   Run scripts   #############################

echo "请确保Xcode已经安装且获取了 license"

# required
#install_zsh
#install_homebrew

# 重启终端，然后再次执行脚本 zsh mac_dev_env_init.sh
init_homebrew
init_zsh


# --- optional ---
#install_autojump
#install_tree

##########################################################################
