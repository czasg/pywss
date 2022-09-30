import json
import socket
import threading


class Context:

    def __init__(self, fd: socket.socket, method, route, version, headers, content):
        self.fd = fd
        self.method = method
        self.route = route
        self.version = version
        self.headers = headers
        self.content = content

        self.response_code = 200
        self.response_headers = {
            "Server-Version": "0.0.1",
        }
        self.response_content = ""

    def set_statuscode(self, code):
        self.response_code = code

    def set_header(self, k, v):
        self.headers[k] = v

    def write(self, data):
        if isinstance(data, str):
            self.response_content = data
        elif isinstance(data, dict):
            self.response_content = json.dumps(data)

    def flush(self):
        first_line = f"HTTP/1.1 {self.response_code} test"
        header_line = "\r\n".join([f"{k}: {v}" for k, v in self.response_headers.items()])
        resp = first_line + "\r\n" + header_line + "\r\n" + "\r\n" + self.response_content
        self.fd.sendall(resp.encode())


class App:

    def __init__(self):
        self.route = {}

    def register(self, method: str, route: str, handler):
        self.route[f"{method.upper()}/{route.strip('/')}"] = handler

    def post(self, route: str, handler):
        self.register("POST", route, handler)

    def _(self, request: socket.socket, address: tuple):
        # print(address)
        try:
            rfd = request.makefile("rb", -1)
            method, route, version = rfd.readline().decode().split()
            # print(method, route, version)
            headers = {}
            while True:
                line = rfd.readline()
                if line == b"\r\n":
                    break
                k, v = line.decode().split(":", 1)
                headers[k.strip()] = v.strip()
            # print(headers)
            content = b""
            content_length = int(headers.get("Content-Length", "0"))
            if content_length:
                content = rfd.read(content_length)
            # print(content)
            ctx = Context(request, method, route, version, headers, content)
            handler = self.route.get(f"{method}{route}", None)
            if handler:
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
            threading.Thread(target=self._, args=(request, address)).start()


def handler(ctx: Context):
    print(ctx.method, ctx.route)
    print(ctx.headers)
    print(ctx.content)
    ctx.write("hello world")
    ctx.flush()


if __name__ == '__main__':
    app = App()
    app.post("/test", handler)
    app.run()
