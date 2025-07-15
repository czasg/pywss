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
- **快速**：引入线程池机制，减少并发场景下线程创建/销毁开销。
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
import time
import pywss

def log_handler(ctx: pywss.Context):
    start_time = time.time()
    ctx.next()
    print(
        f"Route: {ctx.route}, "
        f"Method: {ctx.method}, "
        f"Status: {ctx.response_status_code}, "
        f"Time: {time.time() - start_time:.3f}s"
    )

def handler(ctx: pywss.Context):
  ctx.write("hello~")

def main():
    app = pywss.App()
    app.get("/hello", handler)  # curl localhost:8080/hello
    app.any("*", log_handler, handler)  # curl -X POST localhost:8080/hello
    app.run()

if __name__ == '__main__':
    main()
```
接着启动服务:
```shell
python3 main.py
```

至此，一个简单的 web 应用服务就完成了。

### 2、搭建 MCP 应用
为简化 MCP 工具开发，Pywss 一站式集成 SSE、StreamHTTP 和 MCPO 协议，助你轻松构建全功能服务。
```python
# coding: utf-8
import pywss
from enum import Enum
from pydantic import BaseModel
from pywss.mcp import MCPServer

class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

class DomainReq(BaseModel):  # 定义 DomainReq 请求，必须从 BaseModel 继承
    domain: str
    color: Color

class DomainsReq(BaseModel):  # 定义 DomainsReq 请求，必须从 BaseModel 继承
    domains: list[str]

class DomainMCPServer(MCPServer):  # 定义 DomainMCPServer 服务，必须从 MCPServer 继承

    @pywss.openapi.docs(description="获取单个域名服务", request=DomainReq)  # required
    def tool_get_domain(self, ctx: pywss.Context):
        req: DomainReq = ctx.data.req  # 从 ctx.data.req 获取请求，异常请求会被拦截
        self.handle_success(ctx, {  # handle_success 封装了 jsonrpc2.0 输出规范
            "domain": req.domain,
            "color": req.color
        })

    @pywss.openapi.docs(description="获取批量域名服务", request=DomainsReq)  # required
    def tool_get_domains(self, ctx: pywss.Context):
        req: DomainsReq = ctx.data.req  # 从 ctx.data.req 获取请求，异常请求会被拦截
        self.handle_error(ctx, message="test error")  # handle_error 封装了 jsonrpc2.0 输出规范


mcpServer = DomainMCPServer()

app = pywss.App()
app.openapi()
mcpServer.mount(app.group("/api/v1/mcp"))  # 挂载 mcp 服务，同时指定路由
app.run()
```
接着启动服务:
```shell
python3 main.py
```
- SSE 默认端点 sse：`GET:/api/v1/mcp/sse`
- StreamHttp 默认端点 mcp：`POST:/api/v1/mcp/mcp`
- MCPO 默认端点 tools：
  - `POST:/api/v1/mcp/tools/get_domain` (最后为工具名称)
  - `POST:/api/v1/mcp/tools/get_domains`

更多功能见[在线文档](https://czasg.github.io/pywss/)。
  
<br/>

## Activity

![Alt](https://repobeats.axiom.co/api/embed/0647dce0c169ba858b3592938376e41d20dc3e6f.svg "Repobeats analytics image")
