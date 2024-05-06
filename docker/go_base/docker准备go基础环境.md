# docker准备go基础环境

可以直接执行 build.sh脚本

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

