<div align='center'>

![pywss](./pywss.png)
  
<br/>
  
![Project status](https://img.shields.io/badge/python-3.6+-green.svg)
![PyPI](https://img.shields.io/pypi/v/pywss?color=green)
![Codecov](https://img.shields.io/codecov/c/github/czasg/pywss?token=JSXIQXY1EQ)
[![GitHub issues](https://img.shields.io/github/issues/czasg/pywss)](https://github.com/czasg/pywss/issues)
[![GitHub issues](https://img.shields.io/github/issues-closed/czasg/pywss)](https://github.com/czasg/pywss/issues-closed)
[![GitHub license](https://img.shields.io/github/license/czasg/pywss)](https://github.com/czasg/pywss/blob/main/LICENSE)
  
<br/>
  
</div>

## Pywss 简介

Pywss（发音 /piːwaɪz/，类似 **p~whys**）是一个轻量级的 Python Web 框架，它基于 Python3.6+ 特性构建。

与 Flask、Django 等主流框架不同的是，Pywss 的底层并没有实现 WSGI 接口协议。
其编程风格也更类似于 Gin、Iris 等框架，因此对于熟悉这些框架的开发者来说，Pywss 是一个非常值得探索的项目。

其关键特性有：
- **简单**：拒绝海量参数，减少心智负担。了解上下文 `pywss.Context` 即刻启程。
- **快速**：纯手撸 socket，拒绝中间商赚取性能差价。(实在有性能追求的同学，不妨再探索下其他语言~**Go**~)
- **优雅**：`ctx.next` 真的太优雅了。如果你也和我一样喜欢，那我觉得这件事情，**泰裤辣！！**
- **标准化**：集成了部分 OpenAPI（Swagger）能力，方便开发者快速生成 API 文档并进行调试。
- **支持WebSocket**：开箱即用的 **WebSocket** 能力。
- **接口测试**：开箱即用的 **API 测试模块**，不启动服务也能测试接口功能辣！

**_在线文档_** [**_https://czasg.github.io/pywss/_**](https://czasg.github.io/pywss/)

<br/>

## 快速开始

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

更多功能见[在线文档](https://czasg.github.io/pywss/)。

<br/>

## 特性速览

### 轻巧的中间件机制
```python
import time
import pywss

# 请求日志中间件
def logHandler(ctx: pywss.Context):
    startTime = time.time()
    ctx.next()
    cost = time.time() - startTime
    print(f"{ctx.method} - {ctx.route} - cost: {cost: .2f}")

app = pywss.App()
app.use(logHandler)  # 注册全局日志中间件
app.run()
```

### 原生的依赖注入体验
```python
import pywss

class Repo:
    def get(self):
        return "repo"

class Service:

    def __init__(self, repo: Repo):  # Service 依赖 Repo
        self.repo = repo

    def get(self):
        return "power by " + self.repo.get()

class UserView:

    def __init__(self, service: Service):  # UserView 依赖 Service
        self.srv = service

    def http_get(self, ctx):
        ctx.write(self.srv.get())

app = pywss.App()
app.view("/user", UserView)  # 注册视图路由->自动注入依赖
app.run()
```

### 强大的文件路由机制
见 [文件路由](https://czasg.github.io/pywss/advance/file-route)
