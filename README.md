## Pywss - Python Web/WebSocket Server
![Project status](https://img.shields.io/badge/version-0.1.1-green.svg)

> 重构前版本参考: [v0.0.15](https://github.com/CzaOrz/Pywss/tree/0.0.15) 

Pywss 是一个类似 Gin 风格的后端框架。它没有采用 wsgi 标准，而是基于 socket 实现。

功能支持：   
- [x] 升级 WebSocket
- [x] Http 单元测试
- [x] Party 子路由
- [x] 静态文件服务器

## 一、快速使用手册
### 1、初始化 app
```python
import pywss

app = pywss.App()
app.run()  # 启动服务
```

### 2、绑定路由
```python
import pywss

app = pywss.App()
app.get("/hello", lambda ctx: ctx.write("hello world")) # 注册路由并绑定匿名函数
app.run()
```
短短几行代码就可以启动一个可用的web服务，     
在浏览器打开 http://localhost:8080/hello 即可看到 hello world

### 3、创建子路由
```python
import pywss

def hello(ctx: pywss.Context):
    ctx.write("hello world")

app = pywss.App()

party = app.party("/api/v1")
party.get("/hello", hello)
party.post("/hello", hello)
app.run()
```
可以使用浏览器或者 curl 指令查看：`curl -X POST localhost:8080/api/v1/hello`

### 4、使用中间件
```python
import pywss, time

def hello(ctx: pywss.Context):
    ctx.write("hello world")

def log_handler(ctx: pywss.Context):
    start = time.time()
    ctx.next()  # 调用 next 进入到下一个 handler
    ctx.log.info(f"{time.time()-start}")

app = pywss.App()
app.use(log_handler)  # 注册中间件
app.get("/hello", hello)  # 也可以直接在此注册
app.run()
```
使用中间件时需要调用 ctx.next() 以便继续执行，否则会中断此次请求。

### 5、升级 WebSocket
```python
import pywss

def websocket(ctx: pywss.Context):
    # 升级 WebSocket
    err = pywss.WebsocketContextWrap(ctx)
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
WebSocket 基于 GET 请求升级实现，而 Pywss 则通过 `WebsocketContextWrap` 完成此处升级。    
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

### 6、单元测试
```python
import pywss
import pywss.test

# 初始化app并注册路由
app = pywss.App()
app.get("/test", lambda ctx: ctx.set_status_code(204))

# 基于app创建HttpRequest
req = pywss.test.HttpRequest(app)
# 发起Get请求，获取resp
resp = req.get("/test")
assert resp.status_code == 204
```

## 二、参数说明
### 1、请求参数
* Context
    * `ctx.fd`: 原生 socket 句柄
    * `ctx.method`: 字符串类型，请求方法，如 `GET/POST/PUT/DELETE`
    * `ctx.path`: 字符串类型，原生请求路径，如 `/api/v1/query`
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
