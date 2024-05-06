# 使用 Ubuntu 22.04 作为基础镜像
FROM ubuntu:22.04

# 替换软件源为阿里云的镜像，加快下载速度
RUN sed -i 's@/archive.ubuntu.com/@/mirrors.aliyun.com/@g' /etc/apt/sources.list && \
    sed -i 's@/security.ubuntu.com/@/mirrors.aliyun.com/@g' /etc/apt/sources.list && \
    apt-get clean && \
    apt-get update

# 安装必要的软件包
RUN apt-get install -y git vim make wget xz-utils python3 python3-pip 

# 复制预下载的 Go 压缩包到容器中
COPY go_base_files/go.tar.xz /tmp

# 解压 Go 压缩包并删除压缩文件
RUN tar -xz -C /usr/local -xzf /tmp/go.tar.xz && \
    rm /tmp/go.tar.xz

# 配置环境变量
ENV GOROOT /usr/local/go
ENV PATH $PATH:$GOROOT/bin

# 配置 Go 代理
RUN go env -w GOPROXY=https://goproxy.cn,direct && \
    go version
