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
