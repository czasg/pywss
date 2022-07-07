# mock 服务

1、安装依赖：`pip install pywss>=0.1.1`

2、启动后端服务：`python app.py`

3、启动服务后，使用 curl 或者 浏览器访问以下地址

```shell script
curl http://localhost:8080/mock?body=hello world

curl http://localhost:8080/mock?code=204

curl http://localhost:8080/mock?code=200&body={"name":"pywss","version":"0.1.1"}&type=json
```
