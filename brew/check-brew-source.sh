#!/bin/bash

echo "🔍 检查 Homebrew 源配置"
echo "======================"

echo -e "\n📦 Brew 源:"
cd "$(brew --repo)"
git remote get-url origin

echo -e "\n📦 Core 源:"
cd "$(brew --repo)/Library/Taps/homebrew/homebrew-core"
git remote get-url origin

echo -e "\n📦 Cask 源:"
if [ -d "$(brew --repo)/Library/Taps/homebrew/homebrew-cask" ]; then
    cd "$(brew --repo)/Library/Taps/homebrew/homebrew-cask"
    git remote get-url origin
else
    echo "未安装 homebrew-cask"
fi

echo -e "\n🌐 环境变量:"
echo "HOMEBREW_BOTTLE_DOMAIN=$HOMEBREW_BOTTLE_DOMAIN"
echo "HOMEBREW_BREW_GIT_REMOTE=$HOMEBREW_BREW_GIT_REMOTE"

echo -e "\n✅ 检查完成"