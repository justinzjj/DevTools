#!/bin/bash
###
 # @Author: Justin
 # @Date: 2024-04-10 20:13:55
 # @fielname: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2024-05-06 09:56:33
### 
set -eu

## 清理文件
cleanup() {
    echo "Cleaning up..."
    rm -rf geth_base_files
    echo "Cleanup complete."
}
#中断删除临时文件
trap cleanup SIGINT EXIT


# 创建一个目录来存放所有预下载的文件
mkdir -p geth_base_files
cd geth_base_files

# 下载指定版本的 Geth
echo "正在下载 Geth v1.10.25..."
wget -c https://github.com/ethereum/go-ethereum/archive/refs/tags/v1.10.25.tar.gz -O go-ethereum.tar.gz
if [ $? -ne 0 ]; then
    echo "Geth v1.10.25 下载失败。"
    exit 1
fi

# 检测系统架构并下载相应版本的 Node.js
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        NODEJS_URL="https://nodejs.org/dist/v20.12.1/node-v20.12.1-linux-x64.tar.xz"
        ;;
    arm64)
        NODEJS_URL="https://nodejs.org/dist/v20.12.1/node-v20.12.1-linux-arm64.tar.xz"
        ;;
    *)
        echo "不支持的架构: $ARCH"
        exit 1
        ;;
esac

echo "根据架构 ($ARCH) 下载 Node.js..."
wget -c $NODEJS_URL -O nodejs.tar.xz
if [ $? -ne 0 ]; then
    echo "Node.js 下载失败。"
    exit 1
fi

cd ..
echo "所有必需的文件已准备完毕，开始构建 geth_base Docker 镜像。"

# 构建 Docker 镜像
docker build -t geth_base:1.0 -f geth_base.dockerfile .
if [ $? -eq 0 ]; then
    echo "Docker 镜像 geth_base:1.0 构建成功。"
else
    echo "Docker 镜像 geth_base:1.0 构建失败。"
    exit 1
fi


cleanup