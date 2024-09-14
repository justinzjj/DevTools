# 基于之前构建的 go_base:2.0 镜像
FROM go_base:2.0


# 安装必要的构建工具和库
RUN apt-get update && apt-get install -y xz-utils build-essential python3 python3-pip jq

# 复制指定版本的 Node.js 和 Geth 客户端
COPY geth_base_files/nodejs.tar.xz /tmp/
COPY geth_base_files/go-ethereum.tar.gz /tmp/

# 解压node
# 安装 Node.js
RUN cd /tmp && \
    tar -xvf nodejs.tar.xz -C /usr/local/ && \
    ln -s /usr/local/nodejs/bin/node /usr/local/bin/node && \
    ln -s /usr/local/nodejs/bin/npm /usr/local/bin/npm && \
    ln -s /usr/local/nodejs/bin/node /usr/bin/node && \
    ln -s /usr/local/nodejs/bin/npm /usr/bin/npm && \
    echo 'export PATH=/usr/local/nodejs/bin:$PATH' >> /etc/profile && \
    . /etc/profile && \
    rm -rf /tmp/nodejs.tar.xz

# 安装 solc-select
RUN pip3 install solc-select && \
    solc-select install 0.8.7 && \
    solc-select use 0.8.7 && \
    rm -rf /root/.cache/pip

# 解压、构建并安装 geth
RUN cd /tmp && \
    tar -xvzf go-ethereum.tar.gz && \
    cd go-ethereum-1.10.25 && \
    make geth && \
    mv build /usr/local/geth && \
    cd / && \
    rm -rf /tmp/go-ethereum.tar.gz /tmp/go-ethereum-1.10.25

# 设置环境变量
ENV Geth="/usr/local/geth"
ENV PATH="$PATH:$Geth/bin"