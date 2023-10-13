# luckysheet 在线管理 - mongodb版本

## 1.本地启动说明

### 1.1.安装依赖

```shell script
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.2.启动mongodb服务

docker启动参考：

```shell script
docker run -itd --rm -p 27017:27017 mongo:latest
```

需要注意：

- 程序默认无账号密码，如果配置了账户信息，需要同步更新代码，见`db/mongo.py`文件

### 1.3.服务启动

```shell script
python app.py
```

1. 打开浏览器并访问地址：[http://localhost:8080/](http://localhost:8080/)
2. 注册新用户并登录
3. 点击【NewDocument】按钮创建新的 luckysheet 文档
4. 点击【在线编辑】按钮跳转 luckysheet 编辑页面

此时，luckysheet 数据是持久化的，并且多 luckysheet 拥有独立数据。