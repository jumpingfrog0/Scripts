#!/bin/bash

###
# iOS 开发环境配置脚本
###

############################   Functions   ###############################

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

function InstallRuby_3_2_8() {
    rvm install 3.2.8
    rvm use 3.2.8
    rvm --default use 3.2.8
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
gem 'cocoapods', '~> 1.16.2'
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

#InstallRvm
#InstallRuby_3_2_8

# # 重启终端，然后再次执行脚本 zsh ios_dev_env.sh
InstallBundler
RunBundleInstall
PodSetup

##########################################################################


