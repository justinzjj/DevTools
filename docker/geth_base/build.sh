###
 # @Author: Justin
 # @Date: 2024-04-10 20:59:22
 # @fielname: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2024-05-06 10:00:02
### 
#!/bin/bash
set -eu

echo "开始构建geth_base:1.0镜像..."

# 检查是否存在镜像 go_base:2.0
if docker images | grep -q "go_base:2.0"; then
    echo "镜像 go_base:2.0 已存在，继续执行后续操作。"
    echo "开始构建geth_base:1.0镜像..."
    ./geth_base_init.sh
else
    echo "镜像 go_base:2.0 不存在"
    echo "开始构建go_base:2.0 镜像..."
    # 执行指定脚本，替换以下路径为实际脚本路径
    ./go_base_init.sh
fi




