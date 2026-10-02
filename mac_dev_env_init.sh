#!/bin/bash

# 安装开关：true 安装，false 跳过。
INSTALL_HOMEBREW=true
INSTALL_OH_MY_ZSH=true
INSTALL_ZSH_SYNTAX_HIGHLIGHTING=true
INSTALL_AUTOJUMP=false
INSTALL_TREE=true
INSTALL_RBENV=true
INSTALL_NVM=true
INSTALL_RUBY=true
INSTALL_NODE=true

# 指定要安装的版本。
RUBY_VERSION="3.3.2"
NODE_VERSION="25.9.0"
NVM_VERSION="v0.40.8"

# 安装失败时停止，避免继续写入未成功安装工具的配置。
set -e

ZSH_CONFIG_DIR="${ZDOTDIR:-$HOME}"
ZSH_RC="$ZSH_CONFIG_DIR/.zshrc"
ZSH_PROFILE="$ZSH_CONFIG_DIR/.zprofile"
HOMEBREW_BIN="/opt/homebrew/bin/brew"
RBENV_BIN="/opt/homebrew/bin/rbenv"
export NVM_DIR="$HOME/.nvm"

# 仅使用 Apple Silicon 的 Homebrew 安装位置。
function setup_homebrew() {
    local brew_environment
    if [ ! -x "$HOMEBREW_BIN" ]; then
        echo "未找到 $HOMEBREW_BIN，请将 INSTALL_HOMEBREW 设为 true 或先手动安装。" >&2
        return 1
    fi

    # 官方建议显式指定 shell；配置写入 macOS Zsh 的登录启动文件。
    brew_environment="$("$HOMEBREW_BIN" shellenv bash)"
    eval "$brew_environment"
    mkdir -p "$ZSH_CONFIG_DIR"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> "$ZSH_PROFILE"
}

# https://brew.sh/
function install_homebrew() {
    if [ ! -x "$HOMEBREW_BIN" ]; then
        echo "Trying to install Homebrew..."
        local installer
        installer="$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        /bin/bash -c "$installer"
        setup_homebrew
    else
        echo "Homebrew is already installed."
    fi
}

# https://github.com/ohmyzsh/ohmyzsh#unattended-install
function install_oh_my_zsh() {
    if [ -d "${ZSH:-$HOME/.oh-my-zsh}" ]; then
        echo "Oh My Zsh is already installed."
    else
        echo "Trying to install Oh My Zsh..."
        local installer
        installer="$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
        # 官方自动安装模式：完成后继续执行本脚本，不启动新的 Zsh。
        sh -c "$installer" "" --unattended
    fi
}

# https://formulae.brew.sh/formula/autojump
function install_autojump() {
    if "$HOMEBREW_BIN" list --formula autojump >/dev/null 2>&1; then
        echo "autojump is already installed."
        return 0
    fi

    echo "Trying to install autojump..."
    "$HOMEBREW_BIN" install autojump
    mkdir -p "$ZSH_CONFIG_DIR"
    echo '[ -f /opt/homebrew/etc/profile.d/autojump.sh ] && . /opt/homebrew/etc/profile.d/autojump.sh' >> "$ZSH_RC"
}

# https://formulae.brew.sh/formula/tree
function install_tree() {
    echo "Trying to install tree..."
    "$HOMEBREW_BIN" install tree
}

# https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md
function install_zsh_syntax_highlighting() {
    if "$HOMEBREW_BIN" list --formula zsh-syntax-highlighting >/dev/null 2>&1; then
        echo "zsh-syntax-highlighting is already installed."
        return 0
    fi

    "$HOMEBREW_BIN" install zsh-syntax-highlighting
    mkdir -p "$ZSH_CONFIG_DIR"
    echo 'source /opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' >> "$ZSH_RC"
}

# https://github.com/rbenv/rbenv#installation
function install_rbenv() {
    if "$HOMEBREW_BIN" list --formula rbenv >/dev/null 2>&1; then
        echo "rbenv is already installed."
        return 0
    fi

    "$HOMEBREW_BIN" install rbenv
    mkdir -p "$ZSH_CONFIG_DIR"
    echo 'eval "$(/opt/homebrew/bin/rbenv init - zsh)"' >> "$ZSH_RC"
}

# https://github.com/nvm-sh/nvm#installing-and-updating
function install_nvm() {
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        echo "nvm is already installed."
        return 0
    fi

    local installer
    installer="$(curl -fsSL "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh")"
    # 配置由下面直接追加，禁止安装器自动安装 Node，保持开关独立。
    PROFILE=/dev/null NODE_VERSION="" /bin/bash -c "$installer"
    mkdir -p "$ZSH_CONFIG_DIR"
    echo 'export NVM_DIR="$HOME/.nvm"' >> "$ZSH_RC"
    echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"' >> "$ZSH_RC"
    echo '[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"' >> "$ZSH_RC"
}

# https://github.com/rbenv/rbenv#installing-ruby-versions
function install_ruby() {
    if [ ! -x "$RBENV_BIN" ]; then
        echo "未找到 rbenv，请将 INSTALL_RBENV 设为 true 或先手动安装。" >&2
        return 1
    fi

    # -s 跳过已安装版本；设为用户默认版本，不修改项目 .ruby-version。
    "$RBENV_BIN" install -s "$RUBY_VERSION"
    "$RBENV_BIN" global "$RUBY_VERSION"
}

# https://github.com/nvm-sh/nvm#usage
function install_node() {
    if [ ! -s "$NVM_DIR/nvm.sh" ]; then
        echo "未找到 nvm，请将 INSTALL_NVM 设为 true 或先手动安装。" >&2
        return 1
    fi

    # 当前脚本直接加载 nvm，无需 source 用户的整个 .zshrc。
    . "$NVM_DIR/nvm.sh" --no-use
    nvm install "$NODE_VERSION"
    nvm alias default "$NODE_VERSION"
}

function main() {
    # 先安装并加载 Homebrew，供后续工具安装使用。
    if [ "$INSTALL_HOMEBREW" = true ]; then
        install_homebrew
    fi

    if [ "$INSTALL_OH_MY_ZSH" = true ]; then
        install_oh_my_zsh
    fi

    if [ "$INSTALL_AUTOJUMP" = true ]; then
        install_autojump
    fi

    if [ "$INSTALL_TREE" = true ]; then
        install_tree
    fi

    if [ "$INSTALL_RBENV" = true ]; then
        install_rbenv
    fi

    if [ "$INSTALL_NVM" = true ]; then
        install_nvm
    fi

    if [ "$INSTALL_RUBY" = true ]; then
        install_ruby
    fi

    if [ "$INSTALL_NODE" = true ]; then
        install_node
    fi

    # 官方要求语法高亮在其他插件之后加载，最后追加其配置。
    if [ "$INSTALL_ZSH_SYNTAX_HIGHLIGHTING" = true ]; then
        install_zsh_syntax_highlighting
    fi

    echo "配置完成，请重新打开终端使 Zsh 配置生效。"
}

main "$@"
