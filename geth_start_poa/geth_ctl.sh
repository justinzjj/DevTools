###
 # @Author: Justin
 # @Date: 2024-09-14 11:24:52
 # @fielname: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2024-09-14 12:16:39
### 



#!/bin/bash

source /etc/profile

PWD_FILE="./pwd.txt"


# 处理命令行参数
while getopts ":i:p:r:a:d:g:o:h" opt; do
  case $opt in
    i) CHAIN_ID="$OPTARG" ;;        # 传递CHAIN_ID
    p) CHAIN_PORT="$OPTARG" ;;      # 传递CHAIN_PORT
    r) CHAIN_RPC_PORT="$OPTARG" ;;  # 传递CHAIN_RPC_PORT
    a) AUTHRPC_PORT="$OPTARG" ;;    # 传递AUTHRPC_PORT
    d) DATADIR="$OPTARG" ;;         # 传递DATADIR
    g) GENESIS="$OPTARG" ;;         # 传递GENESIS路径
    o) ACTION="$OPTARG" ;;          # 选择要执行的操作 (init/start/stop/clean/link)
    h) 
        echo "Usage: $0 -i CHAIN_ID -p CHAIN_PORT -r CHAIN_RPC_PORT -a AUTHRPC_PORT -d DATADIR -g GENESIS -o ACTION"
        exit 0
    ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done


# 初始化
function init_chain() {
    echo "Initializing PoA chain..."
    geth --datadir "$DATADIR" init "$GENESIS"
}

# 启动
function start_chain() {
    echo "Starting PoA chain..."
    
    # 使用nohup和后台运行模式启动geth，启动PoA链
    nohup geth \
        --networkid "$CHAIN_ID" \
        --port "$CHAIN_PORT" \
        --datadir "$DATADIR" \
        --nodiscover \
        --ws \
        --ws.addr 0.0.0.0 \
        --ws.port "$CHAIN_RPC_PORT" \
        --ws.api eth,net,web3,personal,admin,txpool,debug,miner \
        --allow-insecure-unlock \
        --authrpc.port "$AUTHRPC_PORT" \
        --unlock "0x88E7270F9c658651803fC63D47812B9d55ae3333, 0xeeee9ef5498D95858d4Fc816613dBd1cA7ACA77F" \
        --password $PWD_FILE \
        --mine \
        > "$DATADIR/chain.log" 2>&1 &
    
    sleep 1s
    
    # 保存geth进程ID到文件，用于稍后停止进程
    chain_pid=$(ps -ef | grep geth | grep -v grep | awk '{print $2}')
    echo "$chain_pid" > "$DATADIR/chain.pid"
    
    echo "PoA chain started with PID: $chain_pid"
}

# 停止
function stop_chain() {
    echo "Stopping PoA chain..."
    
    # 检查pid文件是否存在
    if [ ! -e "$DATADIR/chain.pid" ]; then
        echo "PID file not found"
        exit 1
    fi
    
    # 读取pid文件中的每个PID并杀死相应进程
    while read -r chain_pid; do
        echo "Killing process with PID: $chain_pid"
        kill -9 "$chain_pid"
        sleep 1s
    done < "$DATADIR/chain.pid"
    
    # 删除pid文件
    echo "Removing PID file..."
    rm -fv "$DATADIR/chain.pid"
    
    echo "Chain stopped."
}

# 清除
function clean_chain() {
    echo "Cleaning up PoA chain..."

    # 检查是否存在数据目录
    if [ -d "$DATADIR" ]; then
        # 删除整个数据目录及其所有内容
        echo "Removing all data in $DATADIR..."
        rm -rfv "$DATADIR"
        echo "All chain data cleaned."
    else
        echo "Data directory $DATADIR does not exist."
    fi
}

function link_chain() {
    echo "Linking to PoA ws://127.0.0.1:$CHAIN_RPC_PORT"

    # 使用geth的attach命令连接到指定链的WebSocket端口
    geth attach ws://127.0.0.1:"$CHAIN_RPC_PORT"
}

# 执行指定的操作
case $ACTION in
  init)
    init_chain
    ;;
  start)
    start_chain
    ;;
  stop)
    stop_chain
    ;;
  clean)
    clean_chain
    ;;
  link)
    link_chain
    ;;
  *)
    echo "Invalid action specified. Please choose from init, start, stop, clean, link."
    exit 1
    ;;
esac

echo "Action '$ACTION' completed successfully with CHAIN_ID: $CHAIN_ID, CHAIN_PORT: $CHAIN_PORT, CHAIN_RPC_PORT: $CHAIN_RPC_PORT, AUTHRPC_PORT: $AUTHRPC_PORT"