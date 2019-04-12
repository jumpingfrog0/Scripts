#!/bin/bash

###
# iOS 开发环境配置脚本
###

############################   Functions   ###############################

function InstallRvm() {
    \curl -sSL https://get.rvm.io | bash -s stable --ruby
    source ~/.rvm/scripts/rvm
}

function InstallHomebrew() {
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew tap caskroom/cask
}

function InstallRuby() {
    rvm install 2.3.1
    rvm use 2.3.1
    rvm list
}

function InstallBundler() {
    gem install bundler
}

function RunBundleInstall() {
    # 将配置写入Gemfile
    gemfile_path="${HOME}/Documents/dev/Gemfile"
    echo 'Gemfile initialing...'
	cat > ${gemfile_path}<<EOF
source "https://rubygems.org"
gem 'cocoapods', '~> 1.5.3'
gem 'fastlane', '~> 2.38.1'
EOF

    # bundle install
    current_dir=$PWD
    cd $HOME/Documents/dev
    bundle install
    cd ${current_dir}
}

function InstallCommandLineTools() {

    # oh-my-zsh
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

    # autojump
    brew install autojump
    echo "\n# autojump configuration\n\
    [[ -s `brew --prefix`/etc/autojump.sh ]] && . `brew --prefix`/etc/autojump.sh" >> ~/.zshrc
    source ~/.zshrc

    # tree
    brew install tree
}

function InstallVimPlugins() {
    git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
}

##########################################################################

############################   Run scripts   #############################

InstallRvm
InstallHomebrew
InstallRuby
InstallBundler
RunBundleInstall
InstallCommandLineTools
InstallVimPlugins

##########################################################################


