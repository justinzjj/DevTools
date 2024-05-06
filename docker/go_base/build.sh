###
 # @Author: Justin
 # @Date: 2024-05-06 10:00:29
 # @fielname: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2024-05-06 10:02:39
### 
#!/bin/bash
set -eu

echo "开始构建go_base:2.0 镜像..."

# 检查是否存在镜像 go_base:2.0
if docker images | grep -q "go_base:2.0"; then
    echo "镜像 go_base:2.0 已存在"
else
    echo "镜像 go_base:2.0 不存在"
    echo "开始构建go_base:2.0 镜像..."
    ./go_base_init.sh
fi

