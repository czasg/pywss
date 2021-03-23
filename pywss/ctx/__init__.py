# coding: utf-8
import json


class Ctx:
    __handlerIndex = 0
    __body = None
    __bodyString = None
    __bodyJson = None
    __bodyForm = None

    __responseStatusCode = 200

    def __init__(self, environ, handlers, pathParams):
        self.__environ = environ
        self.__handlers = handlers
        self.__pathParams = pathParams
        self.__responseBody = []
        self.__responseHeaders = {"Content-Type": "text/html"}

    def next(self):
        if self.__handlerIndex >= len(self.__handlers):
            return
        index = self.__handlerIndex
        self.__handlerIndex += 1
        self.__handlers[index](self)

    def isDone(self):
        return self.__handlerIndex >= len(self.__handlers)

    def urlParams(self):
        return

    def pathParams(self):
        return self.__pathParams

    def path(self):
        pass

    def host(self):
        pass

    def remote(self):
        pass

    def referrer(self):
        pass

    def contentType(self):
        pass

    def setContentType(self):
        pass

    def contentLength(self):
        pass

    def statusCode(self):
        return self.__responseStatusCode

    def setStatusCode(self, statusCode=200):
        self.__responseStatusCode = statusCode

    def form(self):
        pass

    def json(self):
        pass

    def body(self):
        pass

    def headers(self):
        pass

    def setHeader(self):
        pass

    def setHeaders(self):
        pass

    def streamWriter(self):
        pass

    def write(self, body, statusCode=200):
        if isinstance(body, bytes):
            self.__responseBody.append(body)
        elif isinstance(body, str):
            self.__responseBody.append(body.encode("utf-8"))
        elif isinstance(body, (dict, list)):
            self.__responseBody.append(json.dumps(body, ensure_ascii=False).encode("utf-8"))
        else:
            pass
        self.setStatusCode(statusCode)

    def responseBody(self):
        return self.__responseBody

    def responseHeaders(self):
        return list(self.__responseHeaders.items())

    def redirect(self):
        pass
