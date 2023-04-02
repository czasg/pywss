## Pywss - Python Web/WebSocket Server

![Project status](https://img.shields.io/badge/python-3.6+-green.svg)
[![codecov](https://codecov.io/gh/czasg/pywss/branch/master/graph/badge.svg?token=JSXIQXY1EQ)](https://codecov.io/gh/czasg/pywss)
[![PyPI version](https://badge.fury.io/py/pywss.svg)](https://badge.fury.io/py/pywss)
[![GitHub issues](https://img.shields.io/github/issues/czasg/pywss)](https://github.com/czasg/pywss/issues)
[![GitHub issues](https://img.shields.io/github/issues-closed/czasg/pywss)](https://github.com/czasg/pywss/issues-closed)
[![GitHub license](https://img.shields.io/github/license/czasg/pywss)](https://github.com/czasg/pywss/blob/main/LICENSE)

**Pywss 是一个轻量级的 Python Web 框架。**     

其主要特性有：   
- [x] **Http/WebSocket**：支持 Http 服务器和 WebSocket 协议升级，能够轻松处理 Web 应用程序的请求和响应。
- [x] **SwaggerUI**：集成了 Swagger UI，方便开发者快速生成 API 文档并进行调试。
- [x] **Middleware**：支持中间件，可方便地扩展框架功能。
- [x] **RouteParty**：提供了 Route Party，能够简单明了地管理路由，让开发者更加专注于业务逻辑的实现。
- [x] **HttpTest**：提供了 Http API 测试功能，能够方便地测试 API 的正确性和性能。

与 Flask、Django 等主流框架不同的是，Pywss 的底层并没有实现 WSGI 接口协议。  
其编程风格更类似于 Gin、Iris 等框架，因此对于熟悉这些框架的开发者来说，Pywss 是一个非常值得探索的项目。


<br/>

## 一、快速开始

### 1、安装 pywss
```shell
pip3 install pywss
```

### 2、搭建 web 应用    
首先创建 `main.py` 文件，并写入以下代码：
```python
import pywss

def handler(ctx: pywss.Context):
  ctx.write("hello~")

def main(port = 8080):
    app = pywss.App()
    app.get("/hi", lambda ctx: ctx.write("hi~"))  # curl localhost:8080/hi
    app.post("/hello", handler)  # curl -X POST localhost:8080/hello
    app.run(port=port)

if __name__ == '__main__':
    main()
```
接着启动服务:
```shell
python3 main.py
```

至此，一个简单的 web 应用服务就完成了。

<br/>

## 二、进阶使用
- [1、路由方法](#1路由方法)
- [2、特殊路由匹配机制](#2特殊路由匹配机制)
- [3、视图机制](#3视图机制)
- [4、路由组](#4路由组)
- [5、中间件](#5中间件)
- [6、升级WebSocket](#升级WebSocket)
- [7、SwaggerUI](#7SwaggerUI)
- [8、静态文件服务器](#8静态文件服务器)
- [9、单元测试](#9单元测试)
- [10、命令行启动](#10命令行启动)

### 1、路由方法
在快速开始中，我们已经看到了一个简单的应用是如何注册路由并绑定业务模块的。

除了上述`get`、`post`方法之外，**Pywss** 还实现了：

|路由方法|说明|
|---|---|
|get|`app.get("/http-get", handler)`|
|post|`app.post("/http-post", handler)`|
|head|`app.head("/http-head", handler)`|
|put|`app.put("/http-put", handler)`|
|delete|`app.delete("/http-delete", handler)`|
|patch|`app.patch("/http-patch", handler)`|
|options|`app.options("/http-options", handler)`|
|any|`app.any("/http-any", handler)`，包括 Get、Post、Head、Put、Delete、Patch、Options 等在内的全部方法|
|view|`app.view("/http-view", ViewObject)`，基于视图风格实现，具体使用见视图部分|
|static|`app.static("/file-server", ".")`，注册静态文件服务，具体使用见静态文件服务部分|

路由处理函数`handler`仅接收一个参数，就是`pywss.Context`。

<br/>

### 2、特殊路由匹配机制
除了上述常规路由方法之外，**特殊路由匹配机制** 也是现代 web 框架必不可少的特点。

|特殊路由匹配机制|说明|
|---|---|
|全等匹配|`app.get("/full/match", handler)`|
|局部匹配|`app.get("/partial/match/{name}", handler)`，注意，局部变量会存储在`ctx.route_params`中|
|头部匹配|`app.get("/head/match/*", handler)`，注意，此处需以 `*` 结尾|

**_注意_**：   
上述匹配机制无法同时生效，且存在优先级，即**全等匹配**优先、其次**局部匹配**、最后**头部匹配**~

<br/>

### 3、视图机制
**Pywss** 通过 `app.view` 实现了简单的视图机制，以便更加友好的支持 Restful 风格代码，参考如下：

```python
import pywss

class UserView:

    def http_get(self, ctx: pywss.Context):
        uid = ctx.route_params["uid"]
        ctx.write({"uid": uid, "msg": "query success"})

    def http_post(self, ctx: pywss.Context):
        uid = ctx.route_params["uid"]
        ctx.write({"uid": uid, "msg": "create success"})

def main():
    app = pywss.App()
    app.view("/api/user/{uid}", UserView())
    app.run()

if __name__ == '__main__':
    main()
```

<br/>

### 4、路由组
**Pywss** 通过 `app.party` 实现了简单的路由组，以便支持在大型项目下的多级路由管理，参考如下。

```python
import pywss

def handler(ctx: pywss.Context):
    ctx.write(ctx.route)

def main():
    app = pywss.App()

    v1 = app.party("/api/v1")  # 创建 /api/v1 路由组
    v1.get("/user", handler)  # /api/v1/user

    v2 = app.party("/api/v1")  # 创建 /api/v2 路由组
    v2.get("/user", handler)  # /api/v2/user

    app.run()

if __name__ == '__main__':
    main()
```

<br/>

### 5、中间件
**Pywss** 通过 `ctx.next` 实现了功能模块的链式调用，在此基础之上，拓展了中间件的能力。

让我们来实现一个简单输出请求耗时的日志中间件。代码参考如下：

```python
import time
import pywss

def logHandler(ctx: pywss.Context):
    start = int(time.time())
    ctx.next()  # 执行下一个业务模块，执行完成后会继续执行后面的代码
    ctx.log.info(f"{ctx.method}{ctx.route} cost: {int(time.time()) - start}")
```

接着我们可以通过以下三种方式来注册中间件服务：
- `app.use(logHandlerMiddleware)`：通过 `use` 方法可以注册全局生效的中间件
- `app.party("/route", logHandlerMiddleware)`：通过 `party` 路由组可以注册局部生效的中间件
- `app.get("/route", logHandlerMiddleware, handler)`：通过绑定指定路由，可以注册指定路由生效的中间件

一份完整的代码参考如下：
```python
import time
import pywss
import random

def logHandler(ctx: pywss.Context):
    start = int(time.time())
    ctx.next()  # 执行下一个业务模块，执行完成后会继续执行后面的代码
    ctx.log.info(f"{ctx.method}{ctx.route} cost: {int(time.time()) - start}")

def main():
    app = pywss.App()
    app.use(logHandler)
    app.get("*", lambda ctx: time.sleep(random.randint(1, 3)))
    app.run()

if __name__ == '__main__':
    main()
```

除此之外，**Pywss** 还内置了部分常用中间件~

```python
import pywss

app = pywss.App()

app.use(
    pywss.NewRecoverHandler(),  # recover
    pywss.NewCORSHandler(),     # cors
    pywss.NewJWTHandler(),      # jwt
)
```

<br/>

### 6、升级WebSocket
**WebSocket** 底层是基于 HTTP GET 升级实现，是长连接的一种实现方式。

**Pywss** 则通过 `WebSocketUpgrade` 完成此处升级。
升级后将激活 `ctx.ws_read` 和 `ctx.ws_write` 两个接口方法，并通过这两个接口方法与客户端进行交互。

让我们来实现一个简单的 **WebSocket** 升级代码，参考如下：

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

def main():
    app = pywss.App()
    app.get("/websocket", websocket)
    app.run()

if __name__ == '__main__':
    main()
``` 

接着让我们模拟客户端，需要 `打开浏览器 -> F12 -> 进入控制台`，输入以下代码：

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

### 7、SwaggerUI
**Pywss** 实现了部分 **OpenAPI** 的能力。

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
        "page_size": ctx.url_params.get("page_size", 10),
        "username": ctx.url_params.get("username", "username"),
        "name": ctx.route_params.get("name", "name"),
        "Auth": ctx.headers.get("Auth", "Auth"),
    })

def main():
    app = pywss.App()
    app.openapi()  # 开启 openapi
    app.post("/hello/{name}", hello)
    app.run()

if __name__ == '__main__':
    main()
```
在启动服务后，
接着打开浏览器，访问 [localhost:8080/docs](http://localhost:8080/docs) 即可看到经典 SwaggerUI 界面。

<br/>

### 8、文件服务
**Pywss** 通过 `app.static` 实现了简单的静态文件服务器，代码参考如下：
```python
import pywss

app = pywss.App()

# 注册静态资源，需要指定文件根目录
app.static("/static", rootDir="/rootDir") 

app.run()
```
启动服务后，可以通过 [localhost:8080/static/index.html](http://localhost:8080/static/index.html) 进行访问

<br/>

### 9、单元测试
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

### 10、命令行启动
如果你只是想快速且简单的起一个服务，那么你还可以通过命令`pywss`的方式：
- 查看帮助指令
```shell
pywss -h
```

- 启动静态文件服务：
    - `--static`表示`本地路径 : 路由前缀`，即将本地路径下的文件映射到指定路由
    - `--port`表示端口号
```shell
pywss --static=".:/" --port=8080
```
通过`http://localhost:8080/`访问  

- 启动web服务：
    - `--route`表示`method : route : code : body`，即指定响应信息
```shell
pywss --route="GET:/hello:200:hello, world" --route="GET:/ok:204:" --port=8080
```
通过`http://localhost:8080/hello`访问

<br/>

## 三、参数说明
### 1、请求参数
* Context
    * `ctx.app`: app
    * `ctx.fd`: `socket.socket`类型，一般用于写操作
    * `ctx.rfd`: `socket.makefile`类型，一般用于读操作
    * `ctx.method`: `str`类型，请求方法，如 `GET/POST/PUT/DELETE`
    * `ctx.url`: `str`类型，请求路径，如 `/api/v1/query?key=value`
    * `ctx.route_params`: `dict`类型，请求路径参数，如 `/api/v1/query/{name}`
    * `ctx.route`: `str`类型，匹配路由的路径，如 `/api/v1/query`
    * `ctx.cookies`: `dict`类型，用于存储请求`cookies`数据
    * `ctx.body()`: `bytes`类型，获取用户请求报文`body`
    * `ctx.json()`: 解析用户请求，等同于`json.loads(self.body())`，需要遵循一定`json`格式
    * `ctx.form()`: 解析用户请求，需要遵循一定`form`格式
    * `ctx.url_params`: `dict`类型，用于存储解析的`query`参数
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
