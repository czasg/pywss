# luckysheet 在线协同编辑 - mongodb版本

## 1.本地启动说明

### 1.1.安装依赖
```shell script
pip3 install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.2.启动mongodb服务
docker启动参考：
```shell script
docker run -itd -p 27017:27017 mongo:latest
```
需要注意：
- 程序默认无账号密码，如果配置了账户信息，需要同步更新代码，见`db.mongo.py`文件

### 1.3.服务启动
```shell script
python3 app.py
```

打开浏览器并访问地址：[http://localhost:8080/static/luckysheet.html](http://localhost:8080/static/luckysheet.html)

同时打开多个浏览器端口，即可完成在线编辑

### 1.4.其他说明
服务引入了数据库存储，故部分操作会实时存储。

但仅支持部分luckysheet的操作，不支持操作会有日志提醒。

其余操作可自行探索。
