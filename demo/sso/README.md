# SSO单点登录服务

前提需要：**配置hosts文件**    
以win为例：修改 `C:\Windows\System32\drivers\etc\hosts` 文件，加入以下内容：
```text
127.0.0.1       sso
127.0.0.1       shopping
127.0.0.1       living
```

## 1.本地启动说明

### 1.1.安装依赖
```shell script
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.2.启动mysql服务
docker启动参考：
```shell script
docker run -itd -p 3306:3306 -e MYSQL_ROOT_PASSWORD="123456" -e MYSQL_DATABASE="sso" mysql:latest
```

### 1.3.启动服务
```shell script
python3 app.py
```

### 1.4.单点登录说明
- `http://sso`：单点登录系统
- `http://living`：模拟的直播系统
- `http://shopping`：模拟的购物系统

我们可以单独访问每一个服务，此时由于没有登录，均会跳转至单点登录系统。

此时仅需要登录其中某一个服务，然后再次登录其他服务时，就会发现已经登录并自动跳转了。


## 2.其他启动方式
docker-compose启动：
```shell script
docker-compose up
```
需要注意：
- mysql启动会有较长的检测时间
