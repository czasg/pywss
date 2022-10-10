# coding: utf-8

"""
服务端搭建
请求报文解析
上下文绑定
响应报文构造
路由注册
"""

import socket
import threading


class Context:

    def __init__(self, request: socket.socket, method, route, version, headers, body):
        self.request = request
        self.method = method
        self.route = route
        self.version = version
        self.headers = headers
        self.body = body

        self.response_body = ""
        self.response_code = 200
        self.response_headers = {
            "Test-Version": "0.0.1"
        }

    def write(self, data):
        self.response_body = data

    def flush(self):
        sep = "\r\n"
        if self.response_body:
            self.response_headers["Content-Length"] = len(self.response_body.encode())
        text = f"""{self.version} {self.response_code} test
{sep.join([f"{k}: {v}" for k, v in self.response_headers.items()])}

{self.response_body}"""
        self.request.sendall(text.encode())


class App:

    def __init__(self):
        self.routes = {}

    def register(self, method, route, handler):
        self.routes[f"{method}{route}"] = handler

    def get(self, route, handler):
        self.register("GET", route, handler)

    def post(self, route, handler):
        self.register("POST", route, handler)

    def handler(self, request: socket.socket, address):
        try:
            rfd = request.makefile("rb", -1)
            # 解析请求报文 - method, route, version
            method, route, version = rfd.readline().decode().strip().split(" ")
            # 解析请求报文 - headers
            headers = {}
            while True:
                line = rfd.readline().decode().strip()
                if not line:
                    break
                k, v = line.split(":", 1)
                headers[k] = v
            # 解析请求报文 - body
            body = b""
            cl = int(headers.get("Content-Length", 0))
            if cl:
                body = rfd.read(cl)

            ctx = Context(request, method, route, version, headers, body)

            handler = self.routes.get(f"{method}{route}", None)
            if not handler:
                ctx.response_code = 404
                ctx.flush()
                return
            handler(ctx)
        except:
            pass
        finally:
            request.close()

    def run(self, host="0.0.0.0", port=8080):
        sock = socket.socket()
        sock.bind((host, port))
        sock.listen()
        print("server start")

        while True:
            request, address = sock.accept()
            threading.Thread(target=self.handler, args=(request, address)).start()


def hello(ctx: Context):
    ctx.write(f"hello world by {ctx.method}{ctx.route}")
    ctx.flush()


if __name__ == '__main__':
    app = App()
    app.get("/hello", hello)
    app.post("/hello", hello)
    app.run()
