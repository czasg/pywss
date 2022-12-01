# SSO单点登录服务

## 1、配置hosts文件  
以win系统为例：修改 `C:\Windows\System32\drivers\etc\hosts` 文件，加入以下内容：
```text
127.0.0.1       sso
127.0.0.1       shopping
127.0.0.1       living
```

## 2、docker-compose启动
打开命令行执行：`docker-compose up`

## 3、单点登录说明
- `http://sso`：单点登录系统
- `http://living`：模拟的直播系统
- `http://shopping`：模拟的购物系统

我们可以单独访问每一个服务，此时由于没有登录，均会跳转至单点登录系统。

此时仅需要登录其中某一个服务，然后再次登录其他服务时，就会发现已经登录并自动跳转了。
