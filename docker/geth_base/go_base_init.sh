###
 # @Author: Justin
 # @Date: 2024-04-10 20:05:58
 # @fielname: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2024-05-06 09:59:34
### 
#!/bin/bash
set -eu

## 清理文件
cleanup() {
    echo "Cleaning up..."
    rm -rf go_base_files
    echo "Cleanup complete."
}
#中断删除临时文件
trap cleanup SIGINT EXIT

# 创建一个目录来存放所有预下载的文件
mkdir -p go_base_files
cd go_base_files


# 检测系统架构并下载相应版本的 go
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        GO_URL="https://golang.google.cn/dl/go1.22.2.linux-amd64.tar.gz"
        ;;
    arm64)
    # 这怎么 arm64 也用 amd64 呢？
        GO_URL="https://golang.google.cn/dl/go1.22.2.linux-amd64.tar.gz"
        ;;
    *)
        echo "不支持的架构: $ARCH"
        exit 1
        ;;
esac

echo "根据架构 ($ARCH) 下载 Go..."
wget -c $GO_URL -O go.tar.xz
if [ $? -ne 0 ]; then
    echo "Go 下载失败。"
    exit 1
fi

# 下载 Go 语言
# 检查下载是否成功
if [ $? -eq 0 ]; then
    echo "Go 1.22.1 下载成功。"
else
    echo "Go 1.22.1 下载失败，退出脚本。"
    exit 1
fi

# 如果有其他必需文件，也可以在这里下载

cd ..
echo "所有必需的文件已准备完毕，开始构建 go_base Docker 镜像。"

# 构建 Docker 镜像
docker build -t go_base:2.0 -f go_base.dockerfile .

# 检查 Docker 镜像是否成功构建
if [ $? -eq 0 ]; then
    echo "Docker 镜像 go_base:2.0 构建成功。"
else
    echo "Docker 镜像 go_base:2.0 构建失败。"
fi

cleanup

