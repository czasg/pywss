## Pywss - Python Web/WebSocket Server
![Project status](https://img.shields.io/badge/version-0.1.4-green.svg)

> pip3 install pywss

Pywss 是一个轻量级的 Python 后端框架。功能清单：   
- [x] websocket upgrade
- [x] openapi
- [x] swagger ui
- [x] route party
- [x] middleware
- [x] static server
- [x] api test

## 一、快速使用手册

- [1、初始化app](#1初始化app)
- [2、绑定路由](#2绑定路由)
- [3、创建子路由](#3创建子路由)
- [4、使用中间件](#4使用中间件)
- [5、升级WebSocket](#5升级WebSocket)
- [6、openapi & swagger ui](#6openapi--swagger-ui)
- [7、静态文件服务器](#7静态文件服务器)
- [8、单元测试](#8单元测试)

### 1、初始化app
```python
import pywss

app = pywss.App()  # 初始化app

app.run(port=8080)  # 启动服务
```

### 2、绑定路由
```python
import pywss

def hello(ctx: pywss.Context):
    ctx.write({"hello": ctx.paths["name"]})

app = pywss.App()

app.get("/hello", lambda ctx: ctx.write({"hello": "world"})) # 注册路由 & 绑定匿名函数

app.post("/hello/{name}", hello) # 注册路由

app.run(port=8080)
```
在终端界面执行：
```shell script
$ curl localhost:8080/hello
{"hello": "world"}

$ curl -X POST localhost:8080/hello/pywss
{"hello": "pywss"}
```

### 3、创建子路由
```python
import pywss

def hello(ctx: pywss.Context):
    ctx.write({"hello": ctx.path})

app = pywss.App()

v1 = app.party("/api/v1")
v1.get("/hello", lambda ctx: ctx.write({"hello": "v1"}))
v1.post("/hello/{name}", hello)

v2 = app.party("/api/v2")
v2.get("/hello", lambda ctx: ctx.write({"hello": "v2"}))
v2.post("/hello/{name}", hello)

app.run(port=8080)
```
在终端界面执行：
```shell script
$ curl localhost:8080/api/v1/hello
{"hello": "v1"}

$ curl -X POST localhost:8080/api/v1/hello/pywss
{"hello": "/api/v1/hello/pywss"}

$ curl localhost:8080/api/v2/hello
{"hello": "v2"}

$ curl -X POST localhost:8080/api/v2/hello/pywss
{"hello": "/api/v2/hello/pywss"}
```

### 4、使用中间件
```python
import pywss, time

def log_handler(ctx: pywss.Context):
    start = time.time()
    ctx.next()  # 调用 next 进入到下一个 handler
    cost = time.time() - start
    if ctx.response_status_code < 300:
        ctx.log.info(cost)
    elif ctx.response_status_code < 400:
        ctx.log.warning(cost)
    else:
        ctx.log.error(cost)

def auth_handler(ctx: pywss.Context):
    if ctx.paths["name"] != "pywss":  # 校验请求参数
        ctx.set_status_code(pywss.StatusUnauthorized)
        return
    ctx.next()

app = pywss.App()

app.use(log_handler)  # 注册全局中间件

app.get("/hello/{name}", auth_handler, lambda ctx: ctx.write({"hello": "world"}))  # 也可以直接在此注册

app.run()
```
支持 `use` 注册全局中间件，也支持单个路由绑定中间件。    
使用中间件时需要调用 `ctx.next()` 以便继续执行，否则会中断此次请求。     

### 5、升级WebSocket
```python
import pywss

def websocket(ctx: pywss.Context):
    # 升级 WebSocket
    err = pywss.WebSocketContextWrap(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    # 轮询获取消息，阻塞式
    while True:
        data = ctx.ws_read()
        ctx.log.info(data)
        ctx.ws_write(b"hello")


app = pywss.App()

app.get("/websocket", websocket)

app.run()
``` 
WebSocket 本质基于 GET 升级实现，Pywss 则通过 `WebSocketContextWrap` 完成此处升级。    
测试需要`打开浏览器 -> F12 -> 控制台`，输入以下代码：
```
ws = new WebSocket("ws://127.0.0.1:8080/websocket");
ws.onmessage = function (ev) {
    console.log(ev.data);
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
ws.onopen = function() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send('hello??')
    }
}
```

其他具体使用场景/用例，可以参考 [多人在线协同编辑luckysheet](./examples/0.1.1/luckysheet)、[多人聊天室](./examples/0.1.1/chat)

### 6、openapi & swagger ui
```python
import pywss

@pywss.openapi.docs(
    summary="hello",
    description="哈喽",
    params={
        "page_size": "页面大小",
        "username:query": "用户名-query",
        "name:path,require": "用户名-path",
        "Auth:header,required": "校验头",
    },
    request={"hello": "world"},
    response={"hello": "world"},
)
def hello(ctx: pywss.Context):
    ctx.write({
        "hello": "world",
        "page_size": ctx.params.get("page_size", 10),
        "username": ctx.params.get("username", "username"),
        "name": ctx.paths.get("name", "name"),
        "Auth": ctx.headers.get("Auth", "Auth"),
    })

app = pywss.App()

app.openapi(  # 开启 openapi
    title="OpenAPI",
    version="0.0.1",
    openapi_json_route="/openapi.json",
    openapi_ui_route="/docs",
)

app.post("/hello/{name}", hello)

app.run()
```
打开浏览器，访问 [localhost:8080/docs](htto://localhost:8080/docs)

### 7、静态文件服务器
```python
import pywss

app = pywss.App()
app.static("/static", rootDir="/rootDir") # 注册静态资源，需要指定文件根目录
app.run()
```
对于如下目录结构时，可以通过 [localhost:8080/static/index.html](http://localhost:8080/static/index.html) 进行访问
```text
- rootDir
    - index.html
    - 200.html
    - 500.html
```

### 8、单元测试
```python
import pywss
import pywss.test

app = pywss.App()

app.get("/test", lambda ctx: ctx.set_status_code(204))

req = pywss.test.HttpRequest(app)  # 基于app创建HttpRequest

resp = req.get("/test")  # 发起Get请求，获取resp

assert resp.status_code == 204
```
可以参考 [pywss单元测试](./test/0.1.1/test_base.py)

## 二、参数说明
### 1、请求参数
* Context
    * `ctx.app`: app
    * `ctx.fd`: socket 句柄
    * `ctx.method`: 字符串类型，请求方法，如 `GET/POST/PUT/DELETE`
    * `ctx.path`: 字符串类型，请求路径，如 `/api/v1/query`
    * `ctx.paths`: 字典类型，请求路径参数，如 `/api/v1/query/{name}`
    * `ctx.route`: 字符串类型，匹配路由的路径，如 `GET/api/v1/query`
    * `ctx.cookies`: 字典类型，表示 cookies
    * `ctx.content`: 原生二进制请求体
    * `ctx.body()`: 字符串类型。等同于 `ctx.content.decode()`
    * `ctx.json()`: 获取 json 请求
    * `ctx.form()`: 获取 form 请求，文件数据也会存放于此
    * `ctx.params`: 字典类型，获取 url 路由参数，类似 `?code=1&callback=2` 会解析成 `{"code": "1", "callback": "2"}`
        * 多个同名会以列表形式存放，`?code=1&code=2` 会解析成 `{"code": ["1", "2"]}`
    * `ctx.headers`: 字典类型，获取 url 请求头

### 2、响应参数
* Context
    * `ctx.set_status_code`: -
    * `ctx.set_header`: -
    * `ctx.set_content_type`: -
    * `ctx.set_cookie`: -
    * `ctx.write`: -
    * `ctx.write_text`: -
    * `ctx.write_json`: -
    * `ctx.write_file`: -
    * `ctx.ws_read`: WebSocket 专用
    * `ctx.ws_write`: WebSocket 专用
    * `ctx.flush`: 一般不需要自己调用
