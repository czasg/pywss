## Pywss - Python Web/WebSocket Server
![Project status](https://img.shields.io/badge/python-3.6|3.7-green.svg)
[![codecov](https://codecov.io/gh/czasg/pywss/branch/master/graph/badge.svg?token=JSXIQXY1EQ)](https://codecov.io/gh/czasg/pywss)

> pip3 install pywss

**Pywss 是一个轻量级的 Python Web 框架。**     

主要特性：   
- [x] WebSocket Upgrade
- [x] OpenAPI & Swagger-UI
- [x] API Test
- [x] Middleware
- [x] Static Server

<details>
  <summary>重点版本迭代说明</summary>

- 0.1.10
  * 修复部分路由BUG
- 0.1.9
  * 默认支持`keep-alive`
- 0.1.7
  * 调整json/form解析
- 0.1.4
  * 修复`signal`无法在子线程注册
- 0.1.3
  * 支持`openapi`
  * 支持`swagger ui`
- 0.1.2
  * 修复`Content-Length`丢失问题
- 0.1.1
  * 项目重构

</details>

<br/>

## 一、快速开始

1、安装 pywss
```shell
pip3 install pywss
```

2、搭建web服务    
创建 main.py 文件，写入以下代码：
```python
import pywss

def hello(ctx: pywss.Context):
  ctx.write("hello world")

def main():
    app = pywss.App()
    app.get("/hello", hello)
    app.run()

if __name__ == '__main__':
    main()
```
启动服务，至此，一个简单的 hello world 服务就启动了。
```shell
python3 main.py
```


3、基于命令行快速启动       
如果你只是想快速且简单的起一个服务，那么你还可以通过命令`pywss`的方式：
- 查看帮助指令
```shell
pywss -h
```
- 启动静态文件服务，指令如下，此时可以通过`http://localhost:8080`访问：
    - `--static`表示`本地路径 : 路由前缀`，即将本地路径下的文件映射到指定路由
    - `--port`表示端口号
```shell
pywss --static=".:/" --port=8080
```
- 启动web服务，指令如下，此时可以通过`http://localhost:8080/hello`访问：
    - `--route`表示`method : route : code : body`，即指定响应信息
```shell
pywss --route="GET:/hello:200:hello, world" --route="GET:/ok:204:" --port=8080
```

<br/>

## 二、进阶使用
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

# 初始化app
app = pywss.App()

# 启动服务
app.run(port=8080)  
```
默认:
- `host="0.0.0.0"`
- `port=8080`

<br/>

### 2、绑定路由
```python
import pywss

def hello(ctx: pywss.Context):
    ctx.write({"hello": ctx.paths["name"]})

app = pywss.App()

# 注册路由 & 绑定匿名函数
app.get("/hello", lambda ctx: ctx.write({"hello": "world"}))

# 注册路由
app.post("/hello/{name}", hello)

app.run(port=8080)
```
路由处理函数`handler`仅接收一个参数，就是`pywss.Context`。

除此之外，路由支持多种匹配方式：  
- `/hello/world`：精确匹配
- `/hello/{world}`：局部匹配（注意：对应路径参数可通过`ctx.paths["world"]`获取`）
- `/hello/*`：模糊匹配（注意：路由最后一位必须是`*`）

在终端界面执行：
```shell script
$ curl localhost:8080/hello
{"hello": "world"}

$ curl -X POST localhost:8080/hello/pywss
{"hello": "pywss"}
```

<br/>

### 3、创建子路由
pywss 支持通过`app.party`来实现丰富的路由管理
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

<br/>

### 4、使用中间件
pywss 支持通过`use`注册全局中间件，也支持单个路由绑定中间件。  

使用中间件时，注意需要调用`ctx.next()`才能继续往后执行，否则会中断此次请求。 
```python
import pywss, time

# 日志中间件，单次请求结束后输出cost耗时 - 根据响应码判断输出不同级别日志
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

# 认证中间件
def auth_handler(ctx: pywss.Context):  
    # 校验请求参数
    if ctx.paths["name"] != "pywss":  
        ctx.set_status_code(pywss.StatusUnauthorized)
        return
    ctx.next()

app = pywss.App()

# 注册全局中间件
app.use(log_handler)  

# 中间件也可以直接路由处注册
app.get("/hello/{name}", auth_handler, lambda ctx: ctx.write({"hello": "world"}))  

app.run()
```

<br/>

### 5、升级WebSocket
WebSocket 本质基于 HTTP GET 升级实现，Pywss 则通过`WebSocketUpgrade`完成此处升级。    

```python
import pywss

def websocket(ctx: pywss.Context):
    # 升级 WebSocket
    err = pywss.WebSocketUpgrade(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    # 轮询获取消息，实际使用场景建议引入心跳/探活机制
    while True:
        data = ctx.ws_read()
        ctx.log.info(data)
        ctx.ws_write(b"hello")


app = pywss.App()

app.get("/websocket", websocket)

app.run()
``` 
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

其他具体使用场景/用例，可以参考 [多人在线协同编辑luckysheet](./demo/luckysheet)、[多人聊天室](./demo/chat)

<br/>

### 6、openapi & swagger ui
```python
import pywss

@pywss.openapi.docs(
    summary="此处是接口摘要 - 可选",
    description="此处是接口描述 - 可选",
    params={
        "page_size": "此处是参数说明",
        "username:query": "可以指定参数属于query(默认参数)",
        "name:path,required": "path表示为路径参数，required表示必填参数",
        "Auth:header,required": "参数支持：query、path、header、cookie",
    },
    request={"请求说明": "此处是请求示例"},
    response={"响应说明": "此处是响应示例"},
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

# 开启 openapi
app.openapi(  
    title="OpenAPI",
    version="0.0.1",
    openapi_json_route="/openapi.json",
    openapi_ui_route="/docs",
)

app.post("/hello/{name}", hello)

app.run()
```
打开浏览器，访问 [localhost:8080/docs](http://localhost:8080/docs)

<br/>

### 7、静态文件服务器
```python
import pywss

app = pywss.App()

# 注册静态资源，需要指定文件根目录
app.static("/static", rootDir="/rootDir") 

app.run()
```
假设已注册目录`/rootDir`结构如下，则可以通过 [localhost:8080/static/index.html](http://localhost:8080/static/index.html) 进行访问
```text
- rootDir
    - index.html
    - 200.html
    - 500.html
```

<br/>

### 8、单元测试
```python
import pywss

app = pywss.App()

app.get("/test", lambda ctx: ctx.set_status_code(204))

# 基于app创建HttpRequest
req = pywss.HttpTestRequest(app)  

# 发起Get请求，获取resp
resp = req.get("/test")  

assert resp.status_code == 204
```
可以参考 [pywss单元测试](test/test_app.py)

<br/>

## 三、参数说明
### 1、请求参数
* Context
    * `ctx.app`: app
    * `ctx.fd`: `socket.socket`类型，一般用于写操作
    * `ctx.rfd`: `socket.makefile`类型，一般用于读操作
    * `ctx.method`: `str`类型，请求方法，如 `GET/POST/PUT/DELETE`
    * `ctx.path`: `str`类型，请求路径，如 `/api/v1/query`
    * `ctx.paths`: `dict`类型，请求路径参数，如 `/api/v1/query/{name}`
    * `ctx.route`: `str`类型，匹配路由的路径，如 `GET/api/v1/query`
    * `ctx.cookies`: `dict`类型，用于存储请求`cookies`数据
    * `ctx.body()`: `bytes`类型，获取用户请求报文`body`
    * `ctx.json()`: 解析用户请求，等同于`json.loads(self.body())`，需要遵循一定`json`格式
    * `ctx.form()`: 解析用户请求，需要遵循一定`form`格式
    * `ctx.params`: `dict`类型，用于存储解析的`query`参数
        * `http://github.com/czasg/pywss?code=1&callback=2`->`{"code": "1", "callback": "2"}`
        * `http://github.com/czasg/pywss?code=1&code=2`->`{"code": ["1", "2"]}`
    * `ctx.headers`: `dict`类型，用于存储解析的`header`参数

### 2、响应参数
* Context
    * `ctx.set_status_code`: 设置响应状态码
    * `ctx.set_header`: 设置响应头
    * `ctx.set_content_type`: 设置响应类型
    * `ctx.set_cookie`: 设置响应`cookie`
    * `ctx.write`: 用于写请求
    * `ctx.write_text`: 同`ctx.write`
    * `ctx.write_json`: 同`ctx.write`
    * `ctx.write_file`: 同`ctx.write`
    * `ctx.ws_read`: WebSocket 读请求，需要`pywss.WebSocketUpgrade`升级后使用
    * `ctx.ws_write`: WebSocket 写请求，需要`pywss.WebSocketUpgrade`升级后使用
    * `ctx.flush`: 一般不需要自己调用
