#!/bin/bash

###
# iOS 开发环境配置脚本
###

############################   Functions   ###############################

function InstallRvm() {
    # Must install homebrew befroe rvm
    \curl -sSL https://get.rvm.io | bash -s stable --ruby
    source ~/.rvm/scripts/rvm
}

function InstallRuby() {
    rvm install 2.7.1
    rvm use 2.7.1
    rvm list
}

function InstallHomebrew() {
    if [ ! `which brew` ]
    then
	echo 'Homebrew not found. Trying to install Homebrew...'
    	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	brew tap caskroom/cask
    fi
}

function InstallBundler() {
    gem install bundler
}

function RunBundleInstall() {
    # 将配置写入Gemfile
    gemfile_path="${HOME}/Documents/dev/Gemfile"
    echo 'Gemfile initialing...'ruby
	cat > ${gemfile_path}<<EOF
source "https://rubygems.org"
gem 'cocoapods', '~> 1.9.0'
# gem 'fastlane', '~> 2.38.1'
EOF

    # bundle install
    current_dir=$PWD
    cd $HOME/Documents/dev
    bundle install
    cd ${current_dir}
}

function InstallZSH() {

    # oh-my-zsh
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
}

##########################################################################

############################   Run scripts   #############################

echo "请确保Xcode已经安装且获取了 license"

InstallHomebrew

#InstallRvm

#InstallRuby
#InstallBundler

#RunBundleInstall

# todo: 以上工具检查是否安装
# todo: 检查 zsh 是否安装
#InstallZSH

##########################################################################


