#!/bin/bash

# ==============================================
# Homebrew 一键换源脚本
# 支持：官方源、中科大源、清华源、阿里源
# ==============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 当前用户
USER_NAME=$(whoami)

# 获取当前时间
current_time() {
    date "+%Y-%m-%d %H:%M:%S"
}

# 打印带颜色的消息
print_message() {
    echo -e "${2}【$(current_time)】$1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_message "错误：未找到 $1 命令" "$RED"
        exit 1
    fi
}

# 检查 Homebrew 是否安装
check_brew() {
    if ! command -v brew &> /dev/null; then
        print_message "错误：Homebrew 未安装" "$RED"
        print_message "请先安装 Homebrew：" "$YELLOW"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# 显示当前源
show_current_source() {
    print_message "📦 当前 Homebrew 源配置：" "$CYAN"
    echo "----------------------------------------"
    
    # Brew 源
    if [ -d "$(brew --repo)" ]; then
        echo -e "${BLUE}Brew 源:${NC}"
        git -C "$(brew --repo)" config --get remote.origin.url || echo "未配置"
    fi
    
    # Core 源
    if [ -d "$(brew --repo)/Library/Taps/homebrew/homebrew-core" ]; then
        echo -e "\n${BLUE}Core 源:${NC}"
        git -C "$(brew --repo)/Library/Taps/homebrew/homebrew-core" config --get remote.origin.url || echo "未配置"
    fi
    
    # Cask 源
    if [ -d "$(brew --repo)/Library/Taps/homebrew/homebrew-cask" ]; then
        echo -e "\n${BLUE}Cask 源:${NC}"
        git -C "$(brew --repo)/Library/Taps/homebrew/homebrew-cask" config --get remote.origin.url || echo "未配置"
    fi
    
    # Cask-versions 源
    if [ -d "$(brew --repo)/Library/Taps/homebrew/homebrew-cask-versions" ]; then
        echo -e "\n${BLUE}Cask-versions 源:${NC}"
        git -C "$(brew --repo)/Library/Taps/homebrew/homebrew-cask-versions" config --get remote.origin.url || echo "未配置"
    fi
    
    # 环境变量
    echo -e "\n${BLUE}环境变量:${NC}"
    echo "HOMEBREW_BOTTLE_DOMAIN=${HOMEBREW_BOTTLE_DOMAIN:-未设置}"
    echo "HOMEBREW_BREW_GIT_REMOTE=${HOMEBREW_BREW_GIT_REMOTE:-未设置}"
    echo "HOMEBREW_CORE_GIT_REMOTE=${HOMEBREW_CORE_GIT_REMOTE:-未设置}"
    
    echo "----------------------------------------"
}

# 切换源函数
switch_source() {
    local source_type=$1
    
    print_message "正在切换到 $source_type 源..." "$GREEN"
    
    case $source_type in
        "official")
            # 官方源
            BREW_REPO="https://github.com/Homebrew/brew.git"
            CORE_REPO="https://github.com/Homebrew/homebrew-core.git"
            CASK_REPO="https://github.com/Homebrew/homebrew-cask.git"
            CASK_VERSIONS_REPO="https://github.com/Homebrew/homebrew-cask-versions.git"
            BOTTLE_DOMAIN=""
            ;;
        "ustc")
            # 中科大源
            BREW_REPO="https://mirrors.ustc.edu.cn/brew.git"
            CORE_REPO="https://mirrors.ustc.edu.cn/homebrew-core.git"
            CASK_REPO="https://mirrors.ustc.edu.cn/homebrew-cask.git"
            CASK_VERSIONS_REPO="https://mirrors.ustc.edu.cn/homebrew-cask-versions.git"
            BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
            ;;
        "tsinghua")
            # 清华源
            BREW_REPO="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
            CORE_REPO="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
            CASK_REPO="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask.git"
            CASK_VERSIONS_REPO="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask-versions.git"
            BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
            ;;
        "aliyun")
            # 阿里云源
            BREW_REPO="https://mirrors.aliyun.com/homebrew/brew.git"
            CORE_REPO="https://mirrors.aliyun.com/homebrew/homebrew-core.git"
            CASK_REPO="https://mirrors.aliyun.com/homebrew/homebrew-cask.git"
            CASK_VERSIONS_REPO="https://mirrors.aliyun.com/homebrew/homebrew-cask-versions.git"
            BOTTLE_DOMAIN="https://mirrors.aliyun.com/homebrew/homebrew-bottles"
            ;;
        *)
            print_message "错误：未知的源类型 '$source_type'" "$RED"
            show_help
            exit 1
            ;;
    esac
    
    # 切换 brew 源
    if [ -d "$(brew --repo)" ]; then
        git -C "$(brew --repo)" remote set-url origin $BREW_REPO
        print_message "✓ Brew 源已切换" "$GREEN"
    fi
    
    # 切换 core 源
    if [ -d "$(brew --repo)/Library/Taps/homebrew/homebrew-core" ]; then
        git -C "$(brew --repo)/Library/Taps/homebrew/homebrew-core" remote set-url origin $CORE_REPO
        print_message "✓ Core 源已切换" "$GREEN"
    fi
    
    # 切换 cask 源
    if [ -d "$(brew --repo)/Library/Taps/homebrew/homebrew-cask" ]; then
        git -C "$(brew --repo)/Library/Taps/homebrew/homebrew-cask" remote set-url origin $CASK_REPO
        print_message "✓ Cask 源已切换" "$GREEN"
    fi
    
    # 切换 cask-versions 源
    if [ -d "$(brew --repo)/Library/Taps/homebrew/homebrew-cask-versions" ]; then
        git -C "$(brew --repo)/Library/Taps/homebrew/homebrew-cask-versions" remote set-url origin $CASK_VERSIONS_REPO
        print_message "✓ Cask-versions 源已切换" "$GREEN"
    fi
    
    # 更新环境变量
    update_environment "$BOTTLE_DOMAIN" "$BREW_REPO" "$CORE_REPO"
    
    print_message "✅ 已成功切换到 $source_type 源" "$GREEN"
    
    # 询问是否更新
    read -p "是否立即执行 brew update？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message "正在更新 Homebrew..." "$CYAN"
        brew update
    fi
}

# 更新环境变量
update_environment() {
    local bottle_domain=$1
    local brew_repo=$2
    local core_repo=$3
    
    # 检测当前 shell
    local shell_rc
    if [[ $SHELL == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.bash_profile"
    fi
    
    # 备份原有配置
    if [ -f "$shell_rc" ]; then
        cp "$shell_rc" "${shell_rc}.brew-backup-$(date +%Y%m%d%H%M%S)"
    fi
    
    # 删除原有的 brew 相关环境变量
    sed -i.bak '/HOMEBREW_BOTTLE_DOMAIN/d' "$shell_rc" 2>/dev/null
    sed -i.bak '/HOMEBREW_BREW_GIT_REMOTE/d' "$shell_rc" 2>/dev/null
    sed -i.bak '/HOMEBREW_CORE_GIT_REMOTE/d' "$shell_rc" 2>/dev/null
    
    # 添加新的环境变量（如果有值）
    if [ -n "$bottle_domain" ]; then
        echo "export HOMEBREW_BOTTLE_DOMAIN=\"$bottle_domain\"" >> "$shell_rc"
        export HOMEBREW_BOTTLE_DOMAIN="$bottle_domain"
    fi
    
    if [ -n "$brew_repo" ]; then
        echo "export HOMEBREW_BREW_GIT_REMOTE=\"$brew_repo\"" >> "$shell_rc"
        export HOMEBREW_BREW_GIT_REMOTE="$brew_repo"
    fi
    
    if [ -n "$core_repo" ]; then
        echo "export HOMEBREW_CORE_GIT_REMOTE=\"$core_repo\"" >> "$shell_rc"
        export HOMEBREW_CORE_GIT_REMOTE="$core_repo"
    fi
    
    # 清理备份文件
    rm -f "${shell_rc}.bak" 2>/dev/null
    
    print_message "✓ 环境变量已更新到 $shell_rc" "$GREEN"
    
    # 提示用户
    echo -e "${YELLOW}提示：环境变量更改需要重新打开终端或执行以下命令生效：${NC}"
    echo "  source $shell_rc"
}

# 测试源速度
test_source_speed() {
    print_message "正在测试各源速度..." "$CYAN"
    echo "----------------------------------------"
    
    # 定义测试的源
    declare -A sources=(
        ["官方源-GitHub"]="https://github.com"
        ["中科大源"]="https://mirrors.ustc.edu.cn"
        ["清华源"]="https://mirrors.tuna.tsinghua.edu.cn"
        ["阿里源"]="https://mirrors.aliyun.com"
    )
    
    for name in "${!sources[@]}"; do
        url="${sources[$name]}"
        echo -n "测试 $name... "
        
        # 使用 curl 测试连接时间
        time_output=$(curl -o /dev/null -s -w "DNS: %{time_namelookup}s | 连接: %{time_connect}s | 传输: %{time_starttransfer}s | 总时间: %{time_total}s\n" $url 2>&1)
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
            echo "  $time_output"
        else
            echo -e "${RED}✗ 连接失败${NC}"
        fi
    done
    
    echo "----------------------------------------"
}

# 显示帮助信息
show_help() {
    echo -e "${CYAN}Homebrew 源管理脚本 v1.0${NC}"
    echo "========================================"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  current              显示当前源配置"
    echo "  switch <source>      切换到指定源"
    echo "  test                 测试各源速度"
    echo "  help                 显示此帮助信息"
    echo ""
    echo "可用源:"
    echo "  official             官方源 (github.com)"
    echo "  ustc                 中科大源 (推荐国内使用)"
    echo "  tsinghua             清华源"
    echo "  aliyun               阿里云源"
    echo ""
    echo "示例:"
    echo "  $0 current           显示当前源"
    echo "  $0 switch ustc       切换到中科大源"
    echo "  $0 test              测试各源速度"
    echo ""
    echo "环境: macOS $(sw_vers -productVersion) | 用户: $USER_NAME"
    echo "========================================"
}

# 主函数
main() {
    # 检查必要命令
    check_command git
    check_command curl
    check_brew
    
    case $1 in
        "current")
            show_current_source
            ;;
        "switch")
            if [ -z "$2" ]; then
                print_message "错误：请指定要切换的源" "$RED"
                show_help
                exit 1
            fi
            show_current_source
            switch_source "$2"
            show_current_source
            ;;
        "test")
            test_source_speed
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"