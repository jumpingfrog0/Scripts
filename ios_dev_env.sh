#!/bin/bash

###
# iOS 开发环境配置脚本
###

############################   Functions   ###############################

function InstallHomebrew() {
    if [ ! `which brew` ]
    then
	echo 'Homebrew not found. Trying to install Homebrew...'
        # 国外的源被墙了
    	#/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
     
        # 使用国内的源
        /bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"

	brew tap caskroom/cask
    source ~/.zprofile
    fi
}

function InstallRvm() {
    # Must install homebrew befroe rvm
    sudo \curl -sSL https://get.rvm.io | bash -s stable --ruby
    source ~/.rvm/scripts/rvm
}

function InstallRuby() {
    rvm install 3.0.0
    rvm use 3.0.0
    rvm --default use 3.0.0
    rvm list
}

function InstallBundler() {
    gem install bundler
}

function RunBundleInstall() {
    # 将配置写入Gemfile
    mkdir "${HOME}/Documents/dev/"
    gemfile_path="${HOME}/Documents/dev/Gemfile"
    echo 'Gemfile writing...'
    echo '' >> ${gemfile_path}
	cat > ${gemfile_path}<<EOF
source "https://rubygems.org"
gem 'cocoapods', '~> 1.11.3'
EOF

    echo 'bundle installing...'
    # bundle install
    current_dir=$PWD
    cd $HOME/Documents/dev
    bundle install
    cd ${current_dir}
}

function PodSetup() {
    pod setup
}

##########################################################################

############################   Run scripts   #############################

echo "请确保Xcode已经安装且获取了 license"
echo "请不要用su命令，安装 brew 不建议使用root权限"

#InstallHomebrew
InstallRvm
InstallRuby
#InstallBundler
#RunBundleInstall
#PodSetup

##########################################################################


