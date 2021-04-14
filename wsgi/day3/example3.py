# coding: utf-8
import loggus
from wsgiref.simple_server import make_server

"""路由模块

主要作用: 用于过滤出符合业务需求的请求
具体作用: 系统初始化时可以注册路由和对应的处理模块，当出现符合业务需求的请求时，进行下一步处理
"""


class _RouteMap:

    def __init__(self):
        self.__staticRouteMap = {}

    def register(self, route, handler):
        self.__staticRouteMap[route] = handler

    def search(self, route):
        return self.__staticRouteMap.get(route.strip('/'), None)


RouteMap = _RouteMap()


class Route:

    def get(self, route, handler):
        route = route.strip().strip("/")
        route = f"GET/{route}"
        RouteMap.register(route, handler)


"""WSGI应用模块

主要作用: 基于wsgiref标准库搭建WSGI服务
具体作用: 配合使用路由和上下文板块，完成业务需求
"""


class Pywss(Route):

    def run(self, host="0.0.0.0", port=8080):
        loggus.withFieldsAuto(host, port).info("server start")
        make_server(host, port, application).serve_forever()


def application(environ, start_response):
    handler = RouteMap.search(f"{environ['REQUEST_METHOD']}{environ['PATH_INFO']}")
    if not handler:
        start_response("404 err", [])
        return [b"page not found"]
    start_response("200 ok", [("Content-Type", "text/html")])
    return [b"Hello, Pywss!"]


if __name__ == '__main__':
    app = Pywss()
    app.get("/hello", lambda ctx: ctx.write("Hello, Pywss!"))
    app.run()
