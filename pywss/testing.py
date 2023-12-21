# coding: utf-8
import socket
import json as _json


class HttpTestResponse:

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
                self.body = "".join(message_list[index:])
                break
            else:
                k, v = msg.strip().split(":", 1)
                self.headers[k] = v.strip()

    def json(self):
        return _json.loads(self.body)

    def __str__(self):
        headers = []
        for k, v in self.headers.items():
            headers.append(f"{k}: {v}")
        header = "\r\n".join(headers)
        return f"{self.http_version} {self.status_code} {self.status_code_msg}\r\n{header}\r\n\r\n{self.body}"


class HttpTestRequest:

    def __init__(self, app):
        self.app = app
        self.method = None
        self.path = None
        self.body = None
        self.headers = {
            "Pywss-Http-Test": "0.0.1",
            "Connection": "close",
        }
        self.app.build()

    def request(self, method, route,
                params=None, cookies=None, headers=None,
                json=None, data=None, files=None):
        data = data or ""
        self.method = method
        self.path = route.strip("?")
        if params:
            if "?" not in self.path:
                self.path = self.path + "?"
            self.path = self.path + "&".join([f"{k}={v}" for k, v in params.items()])
        if cookies:
            self.set_headers({"Cookie": " ".join([f"{k}={v};" for k, v in cookies.items()])})
        if json:
            self.set_headers({"Content-Type": "application/json"})
            data = _json.dumps(json, ensure_ascii=False)
        elif files:
            boundary = "------------------------boundary"
            self.set_headers({"Content-Type": f"multipart/form-data; boundary={boundary[2:]}"})
            for k, v in files.items():
                if isinstance(v, str):
                    v = open(v, "rb")
                if not hasattr(v, "read") and not hasattr(v, "close"):
                    raise Exception("Unsupport File Type")
                data += boundary + "\r\n"
                data += f'Content-Disposition: form-data; name="{k}"; filename="{getattr(v, "name", "")}"' + "\r\n"
                data += 'Content-Type: application/octet-stream' + "\r\n\r\n"
                data += v.read().decode() + "\r\n"
                v.close()
            data += boundary + "--\r\n"
        if isinstance(data, str):
            self.body = data or ""
        elif isinstance(data, dict):
            self.set_headers({"Content-Type": "application/x-www-form-urlencoded"})
            self.body = "&".join([f"{k}={v}" for k, v in data.items()])
        self.set_headers(headers or {})
        return self.build()

    def set_header(self, k, v):
        self.headers[k.title()] = v
        return self

    def set_headers(self, headers):
        for k, v in headers.items():
            self.set_header(k, v)
        return self

    def build(self) -> HttpTestResponse:
        if self.body:
            self.headers.setdefault("Content-Length", len(self.body.encode()))
        header_list = []
        for k, v in self.headers.items():
            header_list.append(f"{k}: {v}")
        header = "\r\n".join(header_list)
        req_message = f"{self.method} {self.path} HTTP/1.1\r\n{header}\r\n\r\n{self.body}"

        s, c = socket.socketpair()
        with s, c:
            c.sendall(req_message.encode())
            self.app.handler_request(s, None)
            resp = c.makefile("rb", -1)
            return HttpTestResponse(resp.readlines())

    def get(self, route, headers=None, json=None, data=None, **kwargs):
        return self.request("GET", route, headers=headers, json=json, data=data, **kwargs)

    def post(self, route, headers=None, json=None, data=None, **kwargs):
        return self.request("POST", route, headers=headers, json=json, data=data, **kwargs)

    def head(self, route, headers=None, json=None, data=None, **kwargs):
        return self.request("HEAD", route, headers=headers, json=json, data=data, **kwargs)

    def put(self, route, headers=None, json=None, data=None, **kwargs):
        return self.request("PUT", route, headers=headers, json=json, data=data, **kwargs)

    def delete(self, route, headers=None, json=None, data=None, **kwargs):
        return self.request("DELETE", route, headers=headers, json=json, data=data, **kwargs)

    def patch(self, route, headers=None, json=None, data=None, **kwargs):
        return self.request("PATCH", route, headers=headers, json=json, data=data, **kwargs)

    def options(self, route, headers=None, json=None, data=None, **kwargs):
        return self.request("OPTIONS", route, headers=headers, json=json, data=data, **kwargs)
