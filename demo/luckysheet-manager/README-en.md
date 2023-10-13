# luckysheet manager - mongodb & sqlite3

## 1.quick start

### 1.1.install package

```shell script
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.2.active mongodb

```shell script
docker run -itd --rm -p 27017:27017 mongo:latest
```

### 1.3.start server

```shell script
python app.py
```

1. Open chrome browser：[http://localhost:8080/](http://localhost:8080/)
2. Register a new user and login.
3. Click the `New Document` button.
4. Click the `在线编辑` link.
5. Open edge browser and repeat the steps above.

At this time, the luckysheet data is persistent, 
and multiple Luckysheets have independent data.