# luckysheet Online Collaborative editing - mongodb version

### 1.1. Install dependencies
```shell script
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.2. Start a mongodb
docker startup reference:
```shell script
docker run -itd --rm -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=root mongo:latest
```
Note:
- Program default enable account password, if you modify the account information, you need to synchronize to update the code, see 'db/mongo.py' file

### 1.3. Start server
```shell script
python3 app.py
```

Open a browser and access address: [http://localhost:8080/static/luckysheet.html] (http://localhost:8080/static/luckysheet.html)

Open multiple browser ports at the same time to complete online editing.

Now that the data is persistent, you can play with it.
