#!/bin/bash
###
 # @Author: Justin
 # @Date: 2025-09-09 09:52:31
 # @filename: install_zsh.sh
 # @version: 1.0
 # @Description: Install Zsh and Oh My Zsh
 # @LastEditTime: 2025-09-09 09:53:43
### 
#!/bin/bash

set -e

echo "🧠 正在识别操作系统类型..."
OS="unknown"

if [ -f /etc/os-release ]; then
    source /etc/os-release
    if [[ "$ID" == "ubuntu" ]]; then
        OS="ubuntu"
    elif [[ "$ID" == "centos" || "$ID_LIKE" == *"rhel"* || "$ID" == "alinux" ]]; then
        OS="rhel"
    fi
fi

echo "📋 检测到操作系统: $OS"

# 安装 zsh git curl
install_dependencies() {
    echo "🔧 安装 Zsh、Git、Curl ..."
    if [[ "$OS" == "ubuntu" ]]; then
        sudo apt update
        sudo apt install -y zsh git curl
    elif [[ "$OS" == "rhel" ]]; then
        sudo dnf install -y zsh git curl
    else
        echo "❌ 不支持的操作系统"
        exit 1
    fi
}

# 安装 oh-my-zsh
install_ohmyzsh() {
    echo "🛠 安装 Oh My Zsh ..."
    export RUNZSH=no
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
}

# 安装插件
install_plugins() {
    echo "📦 安装 zsh-autosuggestions ..."
    git clone https://github.com/zsh-users/zsh-autosuggestions \
        ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

    echo "📦 安装 zsh-syntax-highlighting ..."
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
        ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

    echo "⚙️ 配置插件和主题到 ~/.zshrc ..."
    sed -i 's/^plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc || true
    sed -i 's/^ZSH_THEME=.*/ZSH_THEME="apple"/' ~/.zshrc || echo 'ZSH_THEME="apple"' >> ~/.zshrc
}

# 设置默认 shell
set_default_shell() {
    echo "✅ 设置 zsh 为默认 shell ..."
    chsh -s $(which zsh)
}

# 执行
install_dependencies
install_ohmyzsh
install_plugins
set_default_shell

echo "✅ 安装完成！已启用插件并设置主题为 apple 🍎"
echo "🌀 请运行 'zsh' 或重新打开终端体验 Oh My Zsh 新界面！"