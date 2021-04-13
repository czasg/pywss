# coding: utf-8
import re
import json
import loggus  # pip install loggus

from wsgiref.simple_server import make_server

"""上下文模块

主要作用: 用于承接 WSGI服务 和 WEB应用
具体作用: 进一步解析environ字典，供WEB应用使用，并构造响应数据，返回给WSGI应用
"""


class Ctx:
    __responseStatusCode = 200

    def __init__(self, environ: dict, urlParams: dict):
        self.__environ = environ
        self.__responseBody = []
        self.__responseHeaders = {"Content-Type": "text/html"}
        self.__urlParams = urlParams or {}

        headers = {}
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                k = "-".join([f"{i[:1]}{i.lower()[1:]}" for i in k[5:].split("_")])
                headers[k] = v
        self.__headers = headers

        cookies = {}
        for value in headers.get("Cookie", "").split(";"):
            values = value.strip().split("=", 1)
            if len(values) != 2:
                continue
            cookies[values[0]] = values[1]
        self.__cookies = cookies

    def urlParams(self):
        return self.__urlParams

    def headers(self):
        return self.__headers

    def cookies(self):
        return self.__cookies

    def setStatusCode(self, statusCode=200) -> None:
        self.__responseStatusCode = statusCode

    def setHeader(self, k, v) -> None:
        self.__responseHeaders[k] = v

    def write(self, body, statusCode=200) -> None:
        if isinstance(body, bytes):
            self.__responseBody.append(body)
        elif isinstance(body, str):
            self.__responseBody.append(body.encode("utf-8"))
        elif isinstance(body, (dict, list)):
            self.setHeader("Content-Type", "application/json")
            self.__responseBody.append(json.dumps(body, ensure_ascii=False).encode("utf-8"))
        self.setStatusCode(statusCode)

    def statusCode(self) -> int:
        return self.__responseStatusCode

    def responseBody(self) -> list:
        return self.__responseBody

    def responseHeaders(self) -> list:
        return list(self.__responseHeaders.items())


"""路由模块

主要作用: 用于过滤出符合业务需求的请求
具体作用: 系统初始化时可以注册路由和对应的处理模块，当出现符合业务需求的请求时，进行下一步处理
"""


class _RouteMap:

    def __init__(self):
        self.__staticRouteMap = {}
        self.__dynamicRouteList = []

    def register(self, route, handler):
        if "(?P<" in route:
            regex = re.sub("(\?P<.*?>)\)", "\\1[^/?]*?)", route) + "/?$"
            prefix = re.search("(.*?)\(\?P", route).group(1)
            length = route.count("/")
            self.__dynamicRouteList.append((prefix, length, re.compile(regex).match, handler))
        else:
            self.__staticRouteMap[route] = handler

    def search(self, route):
        inPath = f"{route.strip('/')}"
        if inPath in self.__staticRouteMap:
            return {}, self.__staticRouteMap[inPath], None
        inLength = inPath.count("/")
        for index in range(len(self.__dynamicRouteList)):
            prefix, length, match, handlers = self.__dynamicRouteList[index]
            if length == inLength and inPath.startswith(prefix):
                pathMatch = match(inPath)
                if pathMatch:
                    return pathMatch.groupdict(), handlers, None
        return None, None, "404 by pywss"


RouteMap = _RouteMap()


class Route:

    def __init__(self, route=""):
        self.route = f"/{route.strip().strip('/')}" if route else route
        self.log = loggus.withFields({"module": "Route", "party": route})

    def party(self, route):
        if not route:
            return self
        return Route(f"{self.route}/{route.strip().strip('/')}")

    def __register(self, method, route, handler):
        if not handler:
            return self.log.withFields({"route": route}).panic(f"undefined handlers, ignore!")
        if not route:
            return self.log.withFields({"route": route}).panic(f"undefined route, ignore!")
        route = route.strip().strip("/")
        route = f"{method}{self.route}/{route}"
        RouteMap.register(route, handler)

    def get(self, route, handler):
        self.__register("GET", route, handler)

    def post(self, route, handler):
        self.__register("POST", route, handler)


"""WSGI应用模块

主要作用: 基于wsgiref标准库搭建WSGI服务
具体作用: 配合使用路由和上下文板块，完成业务需求
"""


class Pywss(Route):

    def run(self, host="0.0.0.0", port=8080):
        loggus.withFields({"host": host, "port": port}).info("server start")
        make_server(host, port, application).serve_forever()


def application(environ, start_response):
    urlParams, handler, err = RouteMap.search(f"{environ['REQUEST_METHOD']}{environ['PATH_INFO']}")
    if err:
        start_response(err, [])
        return [b"page not found"]
    ctx = Ctx(environ, urlParams)
    handler(ctx)
    start_response(f"{ctx.statusCode()} by pywss", ctx.responseHeaders())
    return ctx.responseBody()


if __name__ == '__main__':
    app = Pywss()

    v1 = app.party("/api/v1")
    v1.get("/hello/(?P<name>)", lambda ctx: ctx.write({"version": "v1", "hello": ctx.urlParams()}))
    v1.get("/headers", lambda ctx: ctx.write(ctx.headers()))

    v2 = app.party("/api/v2")
    v2.get("/hello/(?P<name>)", lambda ctx: ctx.write({"version": "v2", "hello": ctx.urlParams()}))
    v2.get("/cookies", lambda ctx: ctx.write(ctx.cookies()))

    app.run()
