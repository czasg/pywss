# coding: utf-8
import json
import loggus

from typing import Union
from _io import _IOBase, BufferedReader, BufferedWriter
from collections import defaultdict
from pywss.statuscode import StatusOK, StatusFound
from pywss.websocket import encodeMsg, websocketRead


class Ctx:
    __handlerIndex = 0
    __body = b""
    __bodyJson = None
    __bodyForm = None

    __responseStatusCode = StatusOK

    def __init__(self, environ: dict, handlers: tuple, urlParams: dict):
        self.__environ = environ
        self.__handlers = handlers
        self.__urlParams = urlParams
        self.__responseBody = []
        self.__responseHeaders = {"Content-Type": "text/html"}

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

        if self.contentLength():
            self.__body = self.streamReader().read(self.contentLength())
            self.__bodyString = self.__body.decode("utf-8")

        self.__log = loggus.withFields({"path": self.path(), "remoteAddr": self.remoteAddr()})

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

    def setStatusCode(self, statusCode=StatusOK) -> None:
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

    def headers(self) -> dict:
        return self.__headers

    def setHeader(self, k, v) -> None:
        self.__responseHeaders[k] = v

    def setHeaders(self, headers) -> None:
        self.__responseHeaders.update(headers)

    def streamReader(self) -> BufferedReader:
        return self.__wsgiInput

    def streamWriter(self) -> BufferedWriter:
        return self.__wsgiOutput

    def write(self, body, statusCode=StatusOK) -> None:
        if isinstance(body, bytes):
            self.__responseBody.append(body)
        elif isinstance(body, str):
            self.__responseBody.append(body.encode("utf-8"))
        elif isinstance(body, (dict, list)):
            self.__responseBody.append(json.dumps(body, ensure_ascii=False).encode("utf-8"))
        elif isinstance(body, _IOBase):
            self.__responseBody = self.__environ['wsgi.file_wrapper'](body)
        else:
            pass
        self.setStatusCode(statusCode)

    def responseBody(self) -> list:
        return self.__responseBody

    def responseHeaders(self) -> list:
        return list(self.__responseHeaders.items())

    def redirect(self, url: str, statusCode=StatusFound) -> None:
        if url.startswith("http"):
            pass
        elif url.startswith("/"):
            url = f"{self.__environ.get('wsgi.url_scheme')}://{self.__environ.get('HTTP_HOST')}{url}"
        self.setHeader("Location", url)
        self.setStatusCode(statusCode)

        self.__handlerIndex = len(self.__handlers)
        self.next()

    def ws(self, body) -> None:
        if isinstance(body, bytes):
            self.streamWriter().write(encodeMsg(body))
        elif isinstance(body, str):
            self.streamWriter().write(encodeMsg(body.encode("utf-8")))
        elif isinstance(body, (dict, list)):
            self.streamWriter().write(encodeMsg(json.dumps(body, ensure_ascii=False).encode("utf-8")))
        else:
            pass
        self.streamWriter().flush()

    def wsFill(self) -> None:
        self.__body = websocketRead(self.streamReader())
        self.__bodyString = self.__body.decode("utf-8")
        self.__bodyJson = None
        self.__bodyForm = None

    def log(self) -> loggus.Entry:
        return self.__log

    def setLog(self, log: loggus.Entry):
        self.__log = log
