###
 # @Author: Justin
 # @Date: 2024-09-14 10:04:42
 # @fielname: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2024-09-14 09:07:56
### 

#!/bin/bash

source /etc/profile#!/bin/bash

# 默认端口
CHAIN_PORT=10016
CHAIN_RPC_PORT=10026
AUTHRPC_PORT=10036
CHAIN_DATA="../chaindata/chain"
CHAIN_GENESIS="../chaindata/chain/genesis.json"

# 处理命令行参数
while getopts ":i:p:r:a:h" opt; do
  case $opt in
    i) CHAIN_ID="$OPTARG" ;;          # 必选参数：CHAIN_ID
    p) CHAIN_PORT="$OPTARG" ;;        # 可选参数：CHAIN_PORT
    r) CHAIN_RPC_PORT="$OPTARG" ;;    # 可选参数：CHAIN_RPC_PORT
    a) AUTHRPC_PORT="$OPTARG" ;;      # 可选参数：AUTHRPC_PORT
    h)
      echo "Usage: $0 -i CHAIN_ID [-p CHAIN_PORT] [-r CHAIN_RPC_PORT] [-a AUTHRPC_PORT]"
      exit 0
    ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

# 检查是否提供了必需参数
if [ -z "$CHAIN_ID" ]; then
  echo "Usage: $0 -i CHAIN_ID [-p CHAIN_PORT] [-r CHAIN_RPC_PORT] [-a AUTHRPC_PORT]"
  exit 1
fi

# 执行 geth_init.sh 脚本的 keystore 和 genesis 准备
echo "Running geth_init.sh to prepare keystore and genesis..."
./geth_init.sh -i "$CHAIN_ID" -o both

# 执行 geth_ctl.sh 脚本的 init 和 start
echo "Initializing and starting PoA chain..."
./geth_ctl.sh -i "$CHAIN_ID" -p "$CHAIN_PORT" -r "$CHAIN_RPC_PORT" -a "$AUTHRPC_PORT" -d $CHAIN_DATA -g $CHAIN_GENESIS -o init
./geth_ctl.sh -i "$CHAIN_ID" -p "$CHAIN_PORT" -r "$CHAIN_RPC_PORT" -a "$AUTHRPC_PORT" -d $CHAIN_DATA -g $CHAIN_GENESIS -o start

echo "Geth chain has been initialized and started with CHAIN_ID: $CHAIN_ID, CHAIN_PORT: $CHAIN_PORT, CHAIN_RPC_PORT: $CHAIN_RPC_PORT, AUTHRPC_PORT: $AUTHRPC_PORT"