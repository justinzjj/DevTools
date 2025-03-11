###
 # @Author: Justin
 # @Date: 2025-02-22 21:21:31
 # @filename: 
 # @version: 
 # @Description: 
 # @LastEditTime: 2025-02-22 21:29:37
### 


# 启动 metatube 服务
docker run -d -p 8080:8080 -v $PWD/config:/config --name metatube \
  -e "HTTP_PROXY=http://192.168.1.122:20171" \
  metatube/metatube-server:latest -dsn /config/metatube.db