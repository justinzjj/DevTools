###
 # @Author: Justin
 # @Date: 2025-02-12 20:57:10
 # @filename: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2025-02-12 20:57:11
### 

#!/bin/bash

# 函数：检查压缩文件类型
check_file_type() {
    if [[ "$1" == *.zip* ]]; then
        echo "zip"
    elif [[ "$1" == *.tar* ]]; then
        echo "tar"
    elif [[ "$1" == *.7z* ]]; then
        echo "7z"
    else
        echo "unsupported"
    fi
}

# 函数：解压zip文件
extract_zip() {
    unzip -P "$password" "$1" -d "$2"
}

# 函数：解压tar文件
extract_tar() {
    tar -xf "$1" -C "$2"
}

# 函数：解压7z文件
extract_7z() {
    7z x "$1" -o"$2" -p"$password"
}

# 主脚本逻辑
if [ $# -lt 1 ]; then
    echo "Usage: $0 <file> [destination_directory]"
    exit 1
fi

file="$1"
destination="$2"
password=""

# 如果文件是加密的，需要输入密码
if [ -z "$destination" ]; then
    read -sp "Enter password: " password
    echo
    destination=$(basename "$file" | sed 's/\.[^.]*$//')  # 默认目录名为文件名
fi

# 创建目标目录（如果没有指定目录，则使用文件名作为目录名）
mkdir -p "$destination"

# 检查文件类型并调用相应的解压函数
file_type=$(check_file_type "$file")
case "$file_type" in
    "zip")
        extract_zip "$file" "$destination"
        ;;
    "tar")
        extract_tar "$file" "$destination"
        ;;
    "7z")
        extract_7z "$file" "$destination"
        ;;
    "unsupported")
        echo "Unsupported file type"
        exit 1
        ;;
esac

echo "Extraction complete to $destination"
