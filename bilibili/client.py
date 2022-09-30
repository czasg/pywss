import requests

print(requests.post("http://localhost:8080/test", data="test").text)

""" 演示框架 - hello world & 聊天室 & 在线协同编辑
import pywss

app = pywss.App()
app.get("/", lambda ctx: ctx.write("hello world"))
app.run()
"""

""" 搭架子
1、搭建socket服务端，获取请求报文
2、解析请求报文 method route version\r\nkey: value\r\n\r\ncontent
- method, route, version, headers, content
3、请求信息封装到context中
4、路由模块
5、http响应
"""

""" 如何深入?

"""
