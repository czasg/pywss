# coding: utf-8
import os
import re
import json
import time
import loggus  # pip install loggus

from typing import Union
from datetime import timedelta
from collections import defaultdict
from wsgiref.simple_server import make_server
from _io import _IOBase, BufferedReader, BufferedWriter

"""上下文模块

主要作用: 用于承接 WSGI服务 和 WEB应用
具体作用: 进一步解析environ字典，供WEB应用使用，并构造响应数据，返回给WSGI应用
"""


class Ctx:
    __handlerIndex = 0
    __body = b""
    __bodyJson = None
    __bodyForm = None

    __responseStatusCode = 200

    def __init__(self, environ: dict, handlers: tuple, urlParams: dict):
        self.__ctxValues = {}
        self.__environ = environ
        self.__handlers = handlers
        self.__urlParams = urlParams
        self.__responseBody = []
        self.__responseHeaders = {"Content-Type": "text/html"}
        self.__responseCookies = []

        self.__wsgiInput = environ.get("wsgi.input")
        self.__wsgiOutput = environ.get("wsgi.output")

        urlParams = defaultdict(list)
        for query in environ["QUERY_STRING"].split("&"):
            kv = query.split("=", 1)
            if len(kv) != 2:
                continue
            urlParams[kv[0]].append(kv[1])
        self.__queryParams = dict(urlParams)

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

        if self.contentLength():
            self.__body = self.streamReader().read(self.contentLength())
            self.__bodyString = self.__body.decode("utf-8")

        self.__log = loggus.withFields({"path": self.path(), "remoteAddr": self.remoteAddr()})

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

    def next(self):
        if self.__handlerIndex >= len(self.__handlers):
            return
        index = self.__handlerIndex
        self.__handlerIndex += 1
        self.__handlers[index](self)

    def isDone(self) -> bool:
        return self.__handlerIndex >= len(self.__handlers)

    def handler(self):
        return self.__handlers[-1]

    def middleware(self):
        return self.__handlers[:-1]

    def queryParams(self):
        return self.__queryParams

    def urlParams(self):
        return self.__urlParams

    def path(self):
        return self.__environ.get("PATH_INFO")

    def method(self):
        return self.__environ.get("REQUEST_METHOD")

    def remoteHost(self):
        return self.__environ.get("REMOTE_HOST")

    def remoteAddr(self):
        return self.__environ.get("REMOTE_ADDR")

    def referer(self) -> Union[str, None]:
        return self.__environ.get("HTTP_REFERER")

    def contentType(self) -> str:
        return self.__environ.get("CONTENT_TYPE")

    def setContentType(self, value) -> None:
        self.setHeader("Content-Type", value)

    def contentLength(self) -> int:
        return int(self.__environ.get("CONTENT_LENGTH") or 0)

    def statusCode(self) -> int:
        return self.__responseStatusCode

    def setStatusCode(self, statusCode=200) -> None:
        self.__responseStatusCode = statusCode

    def form(self) -> Union[None, dict]:
        if self.__bodyForm:
            return self.__bodyForm
        if "application/x-www-form-urlencoded" in self.contentType().lower():
            formData = {}
            for kv in self.__bodyString.split("&"):
                kv = kv.split("=", 1)
                if len(kv) != 2:
                    continue
                formData[kv[0]] = kv[1]
            self.__bodyForm = formData
            return formData

    def json(self) -> Union[None, dict, list]:
        if self.__bodyJson:
            return self.__bodyJson
        if "application/json" in self.contentType().lower():
            jsonData = json.loads(self.__bodyString)
            self.__bodyJson = jsonData
            return jsonData

    def body(self, returnType=bytes) -> Union[str, bytes]:
        if returnType == bytes:
            return self.__body
        elif returnType == str:
            return self.__bodyString

    def cookies(self):
        return self.__cookies

    def headers(self) -> dict:
        return self.__headers

    def setHeader(self, k, v) -> None:
        self.__responseHeaders[k] = v

    def setHeaders(self, headers) -> None:
        self.__responseHeaders.update(headers)

    def setCookie(
            self, key, value,
            maxAge: int = None,
            expires: int = None,
            path: str = "/",
            domain: str = None,
            secure: bool = False,
            httpOnly: bool = False,
    ):
        buf = [f"{key}={value}"]
        if isinstance(maxAge, timedelta):
            maxAge = (maxAge.days * 60 * 60 * 24) + maxAge.seconds
        if expires is not None:
            expires = time.gmtime(expires)
        elif maxAge is not None:
            expires = time.gmtime(time.time() + maxAge)
        if expires:
            d = expires
            expires = "%s, %02d%s%s%s%04d %02d:%02d:%02d GMT" % (
                ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[d.tm_wday],
                d.tm_mday,
                "-",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                )[d.tm_mon - 1],
                "-",
                d.tm_year,
                d.tm_hour,
                d.tm_min,
                d.tm_sec,
            )

        for k, v, q in (
                ("Domain", domain, True),
                ("Expires", expires, False),
                ("Max-Age", maxAge, False),
                ("Secure", secure, None),
                ("HttpOnly", httpOnly, None),
                ("Path", path, False),
        ):
            if q is None:
                if v:
                    buf.append(k)
                continue
            if v is None:
                continue
            buf.append(f"{k}={v}")
        self.__responseCookies.append(("Set-Cookie", "; ".join(buf)))

    def streamReader(self) -> BufferedReader:
        return self.__wsgiInput

    def streamWriter(self) -> BufferedWriter:
        return self.__wsgiOutput

    def write(self, body, statusCode=200) -> None:
        if isinstance(body, bytes):
            self.__responseBody.append(body)
        elif isinstance(body, str):
            self.__responseBody.append(body.encode("utf-8"))
        elif isinstance(body, (dict, list)):
            self.setHeader("Content-Type", "application/json")
            self.__responseBody.append(json.dumps(body, ensure_ascii=False).encode("utf-8"))
        elif isinstance(body, _IOBase):
            self.__responseBody = self.__environ['wsgi.file_wrapper'](body)
        else:
            pass
        self.setStatusCode(statusCode)

    def responseBody(self) -> list:
        return self.__responseBody

    def responseHeaders(self) -> list:
        return list(self.__responseHeaders.items()) + self.__responseCookies

    def redirect(self, url: str, statusCode=302) -> None:
        if url.startswith("http"):
            pass
        elif url.startswith("/"):
            url = f"{self.__environ.get('wsgi.url_scheme')}://{self.__environ.get('HTTP_HOST')}{url}"
        self.setHeader("Location", url)
        self.setStatusCode(statusCode)

        self.__handlerIndex = len(self.__handlers)
        self.next()

    def log(self) -> loggus.Entry:
        return self.__log

    def setLog(self, log: loggus.Entry):
        self.__log = log

    def setCtxValue(self, key, value):
        self.__ctxValues[key] = value

    def getCtxValue(self, key, default=None):
        return self.__ctxValues.get(key, default)

    def htmlText(self, filePath):
        if not os.path.exists(filePath):
            self.log().withFields({"FilePath": filePath}).warning("file not exist")
            return
        self.write(open(filePath, "rb"))


"""路由模块

主要作用: 用于过滤出符合业务需求的请求
具体作用: 系统初始化时可以注册路由和对应的处理模块，当出现符合业务需求的请求时，进行下一步处理
"""


class _RouteMap:

    def __init__(self):
        self.__staticRouteMap = {}
        self.__dynamicRouteList = []
        self.__staticDirRouteList = []

    def register(self, route, *handlers):
        if "(?P<" in route:
            regex = re.sub("(\?P<.*?>)\)", "\\1[^/?]*?)", route) + "/?$"
            prefix = re.search("(.*?)\(\?P", route).group(1)
            length = route.count("/")
            self.__dynamicRouteList.append((prefix, length, re.compile(regex).match, handlers))
        else:
            self.__staticRouteMap[route] = handlers

    def registerStaticDir(self, route, *handlers):
        self.__staticDirRouteList.append((route, handlers))

    def search(self, route):
        inPath = f"{route.strip('/')}"
        if inPath in self.__staticRouteMap:
            return {}, self.__staticRouteMap[inPath], None
        for dirRoute, handlers in self.__staticDirRouteList:
            if inPath.startswith(dirRoute):
                return {"path": inPath.replace(dirRoute, "", 1)}, handlers, None
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
        self.handlers = []
        self.log = loggus.withFields({"module": "Route", "party": route})

    def use(self, *handlers):
        self.handlers += list(handlers)

    def party(self, route, *handlers):
        if not route:
            self.use(*handlers)
            return self
        route = Route(f"{self.route}/{route.strip().strip('/')}")
        handlers = self.handlers + list(handlers)
        route.use(*handlers)
        return route

    def __register(self, method, route, *handlers):
        if not handlers:
            return self.log.withFields({"route": route}).warning(f"undefined handlers, ignore!")
        if not route:
            return self.log.withFields({"route": route}).warning(f"undefined route, ignore!")
        route = route.strip().strip("/")
        route = f"{method}{self.route}/{route}"
        handlers = self.handlers + list(handlers)
        RouteMap.register(route, *handlers)

    def get(self, route, *handlers):
        self.__register("GET", route, *handlers)

    def post(self, route, *handlers):
        self.__register("POST", route, *handlers)

    def static(
            self, route, *handlers, root=".", method="GET",
            textHtml="html,txt",
            textCss="css",
            applicationXJavascript="js",
            applicationJson="json,yml,yaml",
            applicationXml="xml",
            imagePng="jpg,jpeg,png,gif",
            default="application/octet-stream",
    ):
        route = route.strip().strip("/")
        route = f"{method}{self.route}/{route}"
        handlers = self.handlers + list(handlers)
        handlers.append(newStaticHandler(
            root,
            textHtml=textHtml,
            textCss=textCss,
            applicationXJavascript=applicationXJavascript,
            applicationJson=applicationJson,
            applicationXml=applicationXml,
            imagePng=imagePng,
            default=default))
        RouteMap.registerStaticDir(route, *handlers)


"""WSGI应用模块

主要作用: 基于wsgiref标准库搭建WSGI服务
具体作用: 配合使用路由和上下文板块，完成业务需求
"""


class Pywss(Route):

    def run(self, host="0.0.0.0", port=8080):
        loggus.withFields({"host": host, "port": port}).info("server start")
        make_server(host, port, application).serve_forever()


def application(environ, start_response):
    pathParams, handlers, err = RouteMap.search(f"{environ['REQUEST_METHOD']}{environ['PATH_INFO']}")
    if err:
        start_response(err, [])
        return [b"page not found"]
    ctx = Ctx(environ, handlers, pathParams)
    ctx.next()
    start_response(f"{ctx.statusCode()} by pywss", ctx.responseHeaders())
    return ctx.responseBody()


"""
中间件
"""


def _ensureToTuple(value):
    if isinstance(value, str):
        return tuple(value.split(","))
    elif isinstance(value, list):
        return tuple(value)
    elif isinstance(value, tuple):
        return value
    return ()


def newStaticHandler(
        root,
        textHtml,
        textCss,
        applicationXJavascript,
        applicationJson,
        applicationXml,
        imagePng,
        default="application/octet-stream"
):
    textHtml = _ensureToTuple(textHtml)
    textCss = _ensureToTuple(textCss)
    applicationXJavascript = _ensureToTuple(applicationXJavascript)
    applicationJson = _ensureToTuple(applicationJson)
    applicationXml = _ensureToTuple(applicationXml)
    imagePng = _ensureToTuple(imagePng)

    def staticHandler(ctx):
        path = ctx.urlParams()["path"]
        file = os.path.join(root, *path.split("/"))
        if os.path.exists(file):
            if file.endswith(textHtml):
                ctx.setContentType("text/html")
            elif file.endswith(textCss):
                ctx.setContentType("text/css")
            elif file.endswith(applicationXJavascript):
                ctx.setContentType("application/x-javascript")
            elif file.endswith(applicationJson):
                ctx.setContentType("application/json")
            elif file.endswith(applicationXml):
                ctx.setContentType("application/xml")
            elif file.endswith(imagePng):
                ctx.setContentType("image/png")
            else:
                ctx.setContentType(default)
            ctx.write(open(file, "rb"))
        else:
            ctx.setStatusCode(403)

    return staticHandler


if __name__ == '__main__':
    app = Pywss()
    app.static("/static", root="./static_file_dir")
    app.get("/index", lambda ctx: ctx.htmlText("./static_file_dir/html/pywss.html"))
    app.run()
