# coding: utf-8
import json as _json
import pywss
import socket


class HttpResponse:

    def __init__(self, message_list):
        self.content = b"".join(message_list)
        self.http_version, self.status_code, self.status_code_msg = None, None, None
        self.headers = {}
        self.body = None
        message_list = [msg.decode() for msg in message_list]
        index = 0
        for msg in message_list:
            index += 1
            if index == 1:
                head = msg.strip()
                self.http_version, self.status_code, self.status_code_msg = head.split(" ", 2)
                self.status_code = int(self.status_code)
            elif msg == "\r\n":
                self.body = "\r\n".join(message_list[index:])
                break
            else:
                k, v = msg.strip().split(":", 1)
                self.headers[k] = v.strip()

    def __str__(self):
        headers = []
        for k, v in self.headers.items():
            headers.append(f"{k}: {v}")
        header = "\r\n".join(headers)
        return f"{self.http_version} {self.status_code} {self.status_code_msg}\r\n{header}\r\n\r\n{self.body}"


class HttpRequest:

    def __init__(self, app: pywss.App):
        self.app = app
        self.method = None
        self.path = None
        self.body = None
        self.headers = None
        self.app.build()

    def request(self, method, route, headers=None, json=None, data=""):
        self.method = method
        self.path = route
        self.headers = {
            "Pywss-Http-Test": "0.0.1",
        }
        self.set_headers(headers or {})
        if json:
            self.set_headers({"Content-Type": "application/json"})
            data = _json.dumps(json, ensure_ascii=False)
        if isinstance(data, str):
            self.body = data
        return self.build()

    def get(self, route, headers=None, json=None, data=""):
        return self.request("GET", route, headers, json, data)

    def post(self, route, headers=None, json=None, data=""):
        return self.request("POST", route, headers, json, data)

    def head(self, route, headers=None, json=None, data=""):
        return self.request("HEAD", route, headers, json, data)

    def put(self, route, headers=None, json=None, data=""):
        return self.request("PUT", route, headers, json, data)

    def delete(self, route, headers=None, json=None, data=""):
        return self.request("DELETE", route, headers, json, data)

    def patch(self, route, headers=None, json=None, data=""):
        return self.request("PATCH", route, headers, json, data)

    def options(self, route, headers=None, json=None, data=""):
        return self.request("OPTIONS", route, headers, json, data)

    def set_header(self, k, v):
        header = []
        for key in k.split("-"):
            header.append(key[0].upper() + key[1:].lower())
        self.headers["-".join(header)] = v
        return self

    def set_headers(self, headers):
        for k, v in headers.items():
            self.set_header(k, v)
        return self

    def build(self) -> HttpResponse:
        header_list = []
        for k, v in self.headers.items():
            header_list.append(f"{k}: {v}")
        header = "\r\n".join(header_list)
        req_message = f"{self.method} {self.path} HTTP/1.1\r\n{header}\r\n\r\n{self.body}"

        s, c = socket.socketpair()
        with s, c:
            c.sendall(req_message.encode())
            self.app._(s, None)
            resp = c.makefile("rb", -1)
            return HttpResponse(resp.readlines())
