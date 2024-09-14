###
 # @Author: Justin
 # @Date: 2024-09-14 11:12:15
 # @fielname: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2024-09-14 07:29:43
### 
#!/bin/bash

# 固定的参数
TARGET_DIR="../chaindata/chain"      # 默认目标目录
SOURCE_FILE="./genesis.json"         # 默认的genesis.json文件路径

# 处理命令行参数
while getopts ":i:o:h" opt; do
  case $opt in
    i) CHAIN_ID="$OPTARG" ;;         # 传递CHAIN_ID
    o) ACTION="$OPTARG" ;;           # 传递操作类型 (keystore/genesis/both)
    h) 
        echo "Usage: $0 -i CHAIN_ID -o ACTION"
        exit 0
    ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

# 检查是否提供了所有必需参数
if [ -z "$CHAIN_ID" ] || [ -z "$ACTION" ]; then
  echo "Usage: $0 -i CHAIN_ID -o ACTION"
  exit 1
fi


# 准备用户 keystore
function prepare_keystore() {
    echo "Preparing keystore..."
    # 检查目标目录是否存在
    if [ ! -d "$TARGET_DIR" ]; then
        echo "Creating directory $TARGET_DIR..."
        mkdir -p "$TARGET_DIR"
    else
        echo "Directory $TARGET_DIR already exists."
    fi

    # 检查当前目录下的keystore文件夹是否存在
    if [ -d "./keystore" ]; then
        echo "Copying keystore files to $TARGET_DIR..."
        cp -r ./keystore "$TARGET_DIR/"
        echo "Keystore files copied successfully."
    else
        echo "No keystore directory found in the current directory."
        exit 1
    fi
}

# 创建genesis.json
function prepare_genesis() {
    echo "Preparing genesis.json with chainId: $CHAIN_ID"

    TARGET_FILE="$TARGET_DIR/genesis.json"

    # 检查并创建目标目录
    if [ ! -d "$TARGET_DIR" ]; then
        echo "Creating directory $TARGET_DIR..."
        mkdir -p "$TARGET_DIR"
    else
        echo "Directory $TARGET_DIR already exists."
    fi

    # 检查源文件是否存在
    if [ ! -f "$SOURCE_FILE" ]; then
        echo "Error: Source file $SOURCE_FILE not found."
        exit 1
    fi

    # 复制genesis.json文件到目标目录
    echo "Copying $SOURCE_FILE to $TARGET_DIR..."
    cp "$SOURCE_FILE" "$TARGET_FILE"

    # 使用jq修改chainId字段
    echo "Modifying chainId to $CHAIN_ID in $TARGET_FILE..."
    jq ".config.chainId = $CHAIN_ID" "$TARGET_FILE" > "$TARGET_FILE.tmp" && mv "$TARGET_FILE.tmp" "$TARGET_FILE"

    echo "chainId modified successfully in $TARGET_FILE"
}


# 执行指定的操作
case $ACTION in
  keystore)
    prepare_keystore
    ;;
  genesis)
    prepare_genesis
    ;;
  both)
    prepare_keystore
    prepare_genesis
    ;;
  *)
    echo "Invalid action specified. Please choose from keystore, genesis, or both."
    exit 1
    ;;
esac

echo "gethinit script completed with CHAIN_ID: $CHAIN_ID, TARGET_DIR: $TARGET_DIR"

