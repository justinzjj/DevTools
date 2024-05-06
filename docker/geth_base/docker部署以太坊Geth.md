# docker部署以太坊GETH

可以直接执行 build.sh脚本



# docker准备go基础环境

## 准备镜像

拉取ubuntu22镜像

```shell
docker pull ubuntu:22.04
```

**运行镜像**：映射一个工作路径

```shell
docker run -it -v ./go_base_files:/workspace --name go_tmp ubuntu:22.04

`-i`：打开STDIN，用于控制台交互，常与-t一起使用

`-t`：分配tty设备，支持终端登陆，默认为false，常与-i一起使用

`-v`：给容器挂载存储卷，挂载到容器的某个目录，这里讲本地的/workspace挂载到了容器的/workspace目录，用来在容器和宿主机之间共享文件

Docker Ubuntu镜像更换apt-get源

```shell
sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
sed -i s@/security.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
apt-get clean
apt-get update
```

安装git等基本依赖

```shell
apt-get install git -y
apt-get install vim -y
apt-get install make -y
apt-get install wget -y
```

## 配置go环境

**下载并解压go**：选择当前最新版本：[Downloads - The Go Programming Language](https://go.dev/dl/?spm=a2c4e.10696291.0.0.24e019a49JMX5H)

```shell
wget -c https://dl.google.com/go/go1.22.1.linux-amd64.tar.gz
tar -xz -C /usr/local -xzf go1.22.1.linux-amd64.tar.gz
```

**配置环境变量**

```shell
vim /etc/profile
# 在文章末尾添加
export GOROOT="/usr/local/go"
export PATH=$PATH:$GOROOT/bin
# 退出 
source /etc/profile
go env -w GOPROXY=https://goproxy.cn
# 用来解锁一些什么内容
go version
#验证生效
```

## 打包镜像

准备工作完成

打包容器作为日后镜像使用

```shell
docker commit -a "justin" -m "base go1.22.1 image" go_tmp go_base:2.0
```

## 配置Docker

```shell
docker run -it -v ./geth_base_files:/workspace --name geth_tmp go_base:2.0
```

`-i`：打开STDIN，用于控制台交互，常与-t一起使用

`-t`：分配tty设备，支持终端登陆，默认为false，常与-i一起使用

`-v`：给容器挂载存储卷，挂载到容器的某个目录，这里讲本地的/workspace挂载到了容器的/workspace目录，用来在容器和宿主机之间共享文件

```shell
source /etc/profile
go env -w GOPROXY=https://goproxy.cn
# 用来解锁一些什么内容
go version
#验证生效
```

## 安装指定版本Geth

1. **访问Geth的GitHub发布页面**：

   打开[Geth的GitHub发布页面](https://github.com/ethereum/go-ethereum/releases)找到需要的版本。

2. **解压并安装**

   ```shell
   tar -xvzf go-ethereum-1.10.25.tar.gz 
   cd go-ethereum-1.10.25
   
   ## 因为 是m1的mac
   export GOARCH=arm64
   
   # 构建
   make geth
   
   # 移动到local
   mv build /usr/local/geth/build
   
   # 添加到环境变量
   vim /etc/profile
   # 在文章末尾添加
   export Geth="/usr/local/geth/build"
   export PATH=$PATH:$Geth/bin
   # 退出 
   source /etc/profile
   
   # 验证
   geth version
   ```

在完成安装后，通过运行`geth version`来验证Geth的安装和版本。

## 安装node

node 官网：[Download | Node.js (nodejs.org)](https://nodejs.org/en/download/)

选择最新版本：Latest LTS Version: **20.11.1** (includes npm 10.2.4)

下载之后丢到workspace里，然后解压

```shell
apt-get update
apt-get install xz-utils
cd /workspace
tar -xvf node-v20.11.1-linux-arm64.tar.xz -C /usr/local/

# 建立软连接 加环境变量也行 都一样
ln -s /usr/local/node-v20.11.1-linux-arm64/bin/node /usr/local/bin/node 
ln -s /usr/local/node-v20.11.1-linux-arm64/bin/npm /usr/local/bin/npm 
 
ln -s /usr/local/node-v20.11.1-linux-arm64/bin/node /usr/bin/node 
ln -s /usr/local/node-v20.11.1-linux-arm64/bin/npm /usr/bin/npm

## 环境变量
vim /etc/profile

# 在文章末尾添加
export PATH=/usr/local/node-v20.11.1-linux-arm64/bin:$PATH
# 推出
source /etc/profile
```

验

```shell
node --version
npm --version
```

## 安装solc

**记得挂上梯子再来安装**

```shell
apt-get update && apt-get upgrade -y
# 安装必要工具
apt-get install -y software-properties-common
# 添加仓库源
add-apt-repository -y ppa:ethereum/ethereum
add-apt-repository -y ppa:ethereum/ethereum-dev

apt-get update

apt-get install solc

# 测试安装正确性
solc --version
```

如果安装失败 就用下面的方法

## 安装solc-select

```shell
apt-get update
apt-get install -y python3 python3-pip

pip3 install solc-select
```

安装并使用对应solc版本

```shell
solc-select install 0.8.7
solc-select use 0.8.7
```

测试安装

```shell
solc --version
```

## 打包镜像

准备工作完成

打包容器作为日后镜像使用

```shell
docker commit -a "justin" -m "base geth1.10.25 image" geth_tmp geth_base:1.0
```



